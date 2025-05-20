import logging
from typing import List, Dict, Union, Optional, Tuple
from navigation.obstacle.point_filter import PointFilter
from navigation.obstacle.obstacle_clusterer import ObstacleClusterer
from navigation.obstacle.avoidance_commander import AvoidanceCommander
from navigation.obstacle.path_planner import PathPlanner
from navigation.obstacle.stats_provider import StatsProvider
from config.shared_config import SHARED, SHARED_LOCK


logging.basicConfig(level=logging.DEBUG)

class ObstacleHandler:
    """장애물 처리 메인 클래스: 각 모듈을 조율."""
    def __init__(self):
        self.point_filter = PointFilter()
        self.clusterer = ObstacleClusterer(
            eps=SHARED['CONFIG_PARAMS']['DBSCAN_EPS'],
            min_samples=SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES']
        )
        self.commander = AvoidanceCommander(
            obstacle_radius=SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']
        )
        self.path_planner = PathPlanner(
            obstacle_radius=SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']
        )
        self.stats_provider = StatsProvider()

    def update_obstacle(self, obstacle_data: Dict) -> Dict[str, str]:
        """장애물 데이터를 업데이트하고 클러스터링 수행."""
        try:
            if not isinstance(obstacle_data, dict):
                raise TypeError("obstacle_data must be a dictionary")
            points = obstacle_data.get('lidarPoints', [])
            filtered_points = self.point_filter.filter_points(points)
            
            with SHARED_LOCK:
                SHARED['lidar_points'] = filtered_points
                SHARED['obstacle_clusters'] = self.clusterer.cluster_obstacles(filtered_points)
                logging.debug(f"Updated obstacles: {len(SHARED['lidar_points'])} points, "
                              f"{len(SHARED['obstacle_clusters'])} clusters")
            
            return {"status": "OK", "message": "Obstacle data updated"}
        except Exception as e:
            logging.error(f"Obstacle update failed: {str(e)}", exc_info=True)
            return {"status": "ERROR", "message": str(e)}

    def get_avoidance_command(self, current_position: Union[List, Tuple], 
                            current_heading: float) -> Optional[Dict[str, Union[str, float]]]:
        """회피 명령 생성."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
        return self.commander.get_avoidance_command(current_position, current_heading, clusters)

    def is_obstacle_in_path(self, curr_x: float, curr_z: float, 
                          lookahead_x: float, lookahead_z: float) -> bool:
        """경로 상 장애물 확인."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
        return self.path_planner.is_obstacle_in_path(curr_x, curr_z, lookahead_x, lookahead_z, clusters)

    def find_alternative_path(self, curr_x: float, curr_z: float, 
                           goal_x: float, goal_z: float) -> Optional[List[Tuple[float, float]]]:
        """대체 경로 생성."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
        return self.path_planner.find_alternative_path(curr_x, curr_z, goal_x, goal_z, clusters)

    def get_obstacle_stats(self) -> Dict[str, Union[int, float]]:
        """장애물 통계 제공."""
        with SHARED_LOCK:
            clusters = SHARED['obstacle_clusters']
            player_pos = SHARED['player_pos'][-1] if SHARED['player_pos'] else [0.0, 0.0]
        return self.stats_provider.get_obstacle_stats(clusters, player_pos)