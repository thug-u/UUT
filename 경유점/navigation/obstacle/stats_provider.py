import numpy as np
from typing import List, Dict, Union

class StatsProvider:
    """장애물 통계 정보 제공."""
    @staticmethod
    def get_obstacle_stats(clusters: List[List[List[float]]], 
                         player_pos: List[float]) -> Dict[str, Union[int, float]]:
        """장애물 통계 정보 제공."""
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