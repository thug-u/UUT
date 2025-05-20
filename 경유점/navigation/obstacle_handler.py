import numpy as np
import logging
from typing import List, Dict, Union, Optional
from sklearn.cluster import DBSCAN
from scipy.spatial import KDTree
from config.shared_config import SHARED, SHARED_LOCK

logging.basicConfig(level=logging.DEBUG)

class ObstacleHandler:
    def __init__(self):
        self.eps = SHARED['CONFIG_PARAMS']['DBSCAN_EPS']
        self.min_samples = SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES']
        self.current_target = None  # 현재 회피 중인 포인트 ([x, z], index)

    def update_obstacle(self, obstacle_data: Dict) -> Dict[str, str]:
        """장애물 데이터를 업데이트하고 DBSCAN 클러스터링 수행."""
        try:
            if not isinstance(obstacle_data, dict):
                raise TypeError("obstacle_data must be a dictionary")
            points = obstacle_data.get('lidarPoints', [])
            filtered_points = self._filter_points(points)
            
            with SHARED_LOCK:
                SHARED['lidar_points'] = filtered_points
                SHARED['obstacle_clusters'] = self._cluster_obstacles(filtered_points)
                logging.debug(f"Updated obstacles: {len(SHARED['lidar_points'])} points, "
                              f"{len(SHARED['obstacle_clusters'])} clusters")
            
            return {"status": "OK", "message": "Obstacle data updated"}
        except Exception as e:
            logging.error(f"Obstacle update failed: {str(e)}", exc_info=True)
            return {"status": "ERROR", "message": str(e)}

    def _filter_points(self, points: List[Dict]) -> List[Dict]:
        filtered = [
            p for p in points
            if isinstance(p, dict) and 
            isinstance(p.get('position'), dict) and
            'x' in p['position'] and 'z' in p['position'] and
            0.05 < np.sqrt(p['position']['x']**2 + p['position']['z']**2) < 100.0
            # isDetected 조건 제거
        ]
        logging.debug(f"Filtered lidar points: {len(filtered)}/{len(points)}")
        return filtered

    def _adjust_eps(self, points: np.ndarray) -> float:
        """포인트 간 평균 거리를 기반으로 eps 동적 조정."""
        if not points.size:
            return self.eps
        kdtree = KDTree(points)
        distances, _ = kdtree.query(points, k=2)
        avg_dist = np.mean(distances[:, 1])
        return max(1.0, min(5.0, avg_dist * 1.5))

    def _cluster_obstacles(self, points: List[Dict]) -> List[List[List[float]]]:
        """DBSCAN으로 장애물 클러스터링."""
        if not points:
            return []
        try:
            coords = [[p['position']['x'], p['position']['z']] for p in points]
            coords = np.array(coords)
            
            with SHARED_LOCK:
                eps = self._adjust_eps(coords)  # 동적 eps
                min_samples = SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES']
            
            db = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
            labels = db.labels_
            clusters = []
            for label in set(labels) - {-1}:  # 노이즈(-1) 제외
                cluster_points = [coords[i].tolist() for i in range(len(coords)) if labels[i] == label]
                clusters.append(cluster_points)
            
            logging.debug(f"Clustered {len(clusters)} obstacle clusters")
            return clusters
        except Exception as e:
            logging.error(f"Clustering failed: {str(e)}", exc_info=True)
            return []

    def get_avoidance_command(self, current_position: Union[List, tuple], 
                            current_heading: float) -> Optional[Dict[str, Union[str, float]]]:
        """장애물 회피 명령 생성."""
        if not isinstance(current_position, (list, tuple)) or len(current_position) != 2:
            logging.debug("Invalid position")
            self.current_target = None
            return None

        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
            obstacle_radius = SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']
        
        if not clusters:
            logging.debug("No obstacle clusters")
            self.current_target = None
            return None

        current_pos = np.array(current_position)
        min_distance = float('inf')
        nearest_point = None
        nearest_cluster_idx = None

        # 가장 가까운 클러스터 포인트 찾기
        for i, cluster in enumerate(clusters):
            cluster_points = np.array(cluster)
            centroid = np.mean(cluster_points, axis=0)  # 클러스터 중심
            distance = np.linalg.norm(centroid - current_pos)
            if distance < min_distance:
                min_distance = distance
                nearest_point = centroid
                nearest_cluster_idx = i

        # 현재 타겟 유지 여부
        if self.current_target:
            target_point, target_idx = self.current_target
            if target_idx < len(clusters):
                dist = np.linalg.norm(target_point - current_pos)
                if dist < obstacle_radius * 2.0:  # 아직 회피 중
                    nearest_point = target_point
                    min_distance = dist
                    nearest_cluster_idx = target_idx

        self.current_target = (nearest_point, nearest_cluster_idx) if nearest_point is not None else None

        if min_distance < obstacle_radius:
            return {"move": "STOP", "weight": 1.0}
        elif min_distance < obstacle_radius * 1.5:
            return {"move": "SLOW_DOWN", "weight": min_distance / (obstacle_radius * 1.5)}

        rel_x = nearest_point[0] - current_pos[0]
        rel_z = nearest_point[1] - current_pos[1]
        angle_to_point = np.arctan2(rel_z, rel_x) - np.radians(current_heading)
        angle_to_point = ((angle_to_point + np.pi) % (2 * np.pi) - np.pi)  # Normalize to [-pi, pi]
        weight = min(1.0, min_distance / (obstacle_radius * 3.0))
        move = "TURN_LEFT" if 0 <= angle_to_point < np.pi else "TURN_RIGHT"
        
        logging.debug(f"Avoidance: move={move}, weight={weight:.2f}, distance={min_distance:.2f}")
        return {"move": move, "weight": weight}

    def is_obstacle_in_path(self, curr_x: float, curr_z: float, 
                          lookahead_x: float, lookahead_z: float) -> bool:
        """경로 상에 장애물 존재 여부 확인."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
            obstacle_radius = SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']

        if not clusters or not all(isinstance(x, (int, float)) for x in [curr_x, curr_z, lookahead_x, lookahead_z]):
            return False

        path_vec = np.array([lookahead_x - curr_x, lookahead_z - curr_z])
        path_start = np.array([curr_x, curr_z])
        path_length = np.linalg.norm(path_vec)
        if path_length == 0:
            return False

        for cluster in clusters:
            for point in cluster:
                to_point = np.array(point) - path_start
                projection = np.dot(to_point, path_vec) / path_length
                if projection < 0 or projection > path_length:
                    continue
                closest_point = path_start + (projection / path_length) * path_vec
                dist_to_path = np.linalg.norm(np.array(point) - closest_point)
                if dist_to_path < obstacle_radius:
                    return True

        return False

    def find_alternative_path(self, curr_x: float, curr_z: float, 
                           goal_x: float, goal_z: float) -> Optional[List[tuple]]:
        """장애물을 피해 목표까지의 대체 경로 생성."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
            obstacle_radius = SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']

        points = np.array([point for cluster in clusters for point in cluster])
        if not points.size:
            return [(goal_x, goal_z)]

        kdtree = KDTree(points)
        path = [(curr_x, curr_z)]
        current = np.array([curr_x, curr_z])
        goal = np.array([goal_x, goal_z])

        while np.linalg.norm(current - goal) > obstacle_radius:
            direction = (goal - current) / np.linalg.norm(goal - current)
            next_point = current + direction * obstacle_radius
            dist, _ = kdtree.query(next_point)
            if dist < obstacle_radius:
                perp_vec = np.array([-direction[1], direction[0]])
                left_point = next_point + perp_vec * obstacle_radius
                right_point = next_point - perp_vec * obstacle_radius
                left_dist, _ = kdtree.query(left_point)
                right_dist, _ = kdtree.query(right_point)
                next_point = left_point if left_dist > right_dist else right_point
            path.append((next_point[0], next_point[1]))
            current = next_point
            if len(path) > 100:  # 무한 루프 방지
                break

        path.append((goal_x, goal_z))
        logging.debug(f"Alternative path generated with {len(path)} points")
        return path

    def get_obstacle_stats(self) -> Dict[str, Union[int, float]]:
        """장애물 통계 정보 제공 (layout.py의 통계 패널 지원)."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
            player_pos = SHARED['player_pos'][-1] if SHARED['player_pos'] else [0.0, 0.0]

        num_obstacles = len(clusters)
        avg_distance = 0.0
        if clusters:
            distances = []
            current_pos = np.array(player_pos)
            for cluster in clusters:
                centroid = np.mean(np.array(cluster), axis=0)
                distance = np.linalg.norm(centroid - current_pos)
                distances.append(distance)
            avg_distance = np.mean(distances) if distances else 0.0

        return {
            "obstacle_count": num_obstacles,
            "average_distance": round(avg_distance, 2)
        }