import numpy as np
import logging
from typing import List, Optional, Tuple
from scipy.spatial import KDTree

logging.basicConfig(level=logging.DEBUG)

class PathPlanner:
    """경로 상 장애물 확인 및 대체 경로 생성."""
    def __init__(self, obstacle_radius: float):
        self.obstacle_radius = obstacle_radius

    def is_obstacle_in_path(self, curr_x: float, curr_z: float, 
                          lookahead_x: float, lookahead_z: float, 
                          clusters: List[List[List[float]]]) -> bool:
        """경로 상에 장애물 존재 여부 확인."""
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
                if dist_to_path < self.obstacle_radius:
                    return True

        return False

    def find_alternative_path(self, curr_x: float, curr_z: float, 
                           goal_x: float, goal_z: float, 
                           clusters: List[List[List[float]]]) -> Optional[List[Tuple[float, float]]]:
        """장애물을 피해 목표까지의 대체 경로 생성."""
        points = np.array([point for cluster in clusters for point in cluster])
        if not points.size:
            return [(goal_x, goal_z)]

        kdtree = KDTree(points)
        path = [(curr_x, curr_z)]
        current = np.array([curr_x, curr_z])
        goal = np.array([goal_x, goal_z])

        while np.linalg.norm(current - goal) > self.obstacle_radius:
            direction = (goal - current) / np.linalg.norm(goal - current)
            next_point = current + direction * self.obstacle_radius
            dist, _ = kdtree.query(next_point)
            if dist < self.obstacle_radius:
                perp_vec = np.array([-direction[1], direction[0]])
                left_point = next_point + perp_vec * self.obstacle_radius
                right_point = next_point - perp_vec * self.obstacle_radius
                left_dist, _ = kdtree.query(left_point)
                right_dist, _ = kdtree.query(right_point)
                next_point = left_point if left_dist > right_dist else right_point
            path.append((next_point[0], next_point[1]))
            current = next_point
            if len(path) > 100:
                break

        path.append((goal_x, goal_z))
        logging.debug(f"Alternative path generated with {len(path)} points")
        return path