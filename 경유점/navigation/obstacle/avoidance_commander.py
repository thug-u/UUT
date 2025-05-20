import numpy as np
import logging
from typing import List, Dict, Union, Optional, Tuple

logging.basicConfig(level=logging.DEBUG)

class AvoidanceCommander:
    """장애물 회피 명령 생성."""
    def __init__(self, obstacle_radius: float):
        self.obstacle_radius = obstacle_radius
        self.current_target = None  # ([x, z], index)

    def get_avoidance_command(self, current_position: Union[List, Tuple], 
                            current_heading: float, 
                            clusters: List[List[List[float]]]) -> Optional[Dict[str, Union[str, float]]]:
        """장애물 회피 명령 생성."""
        if not isinstance(current_position, (list, tuple)) or len(current_position) != 2:
            logging.debug("Invalid position")
            self.current_target = None
            return None

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
            centroid = np.mean(cluster_points, axis=0)
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
                if dist < self.obstacle_radius * 2.0:
                    nearest_point = target_point
                    min_distance = dist
                    nearest_cluster_idx = target_idx

        self.current_target = (nearest_point, nearest_cluster_idx) if nearest_point is not None else None

        if min_distance < self.obstacle_radius:
            return {"move": "STOP", "weight": 1.0}
        elif min_distance < self.obstacle_radius * 1.5:
            return {"move": "SLOW_DOWN", "weight": min_distance / (self.obstacle_radius * 1.5)}

        rel_x = nearest_point[0] - current_pos[0]
        rel_z = nearest_point[1] - current_pos[1]
        angle_to_point = np.arctan2(rel_z, rel_x) - np.radians(current_heading)
        angle_to_point = ((angle_to_point + np.pi) % (2 * np.pi) - np.pi)
        weight = min(1.0, min_distance / (self.obstacle_radius * 3.0))
        move = "TURN_LEFT" if 0 <= angle_to_point < np.pi else "TURN_RIGHT"
        
        logging.debug(f"Avoidance: move={move}, weight={weight:.2f}, distance={min_distance:.2f}")
        return {"move": move, "weight": weight}