import numpy as np
import logging
from typing import Dict, List
from sklearn.cluster import DBSCAN
from scipy.spatial import KDTree
from config.shared_config import SHARED, SHARED_LOCK

logging.basicConfig(level=logging.DEBUG)

class ObstacleClusterer:
    """DBSCAN을 사용한 장애물 클러스터링."""
    def __init__(self, eps: float, min_samples: int):
        self.eps = eps
        self.min_samples = min_samples

    def _adjust_eps(self, points: np.ndarray) -> float:
        """포인트 간 평균 거리를 기반으로 eps 동적 조정."""
        if not points.size:
            return self.eps
        kdtree = KDTree(points)
        distances, _ = kdtree.query(points, k=2)
        avg_dist = np.mean(distances[:, 1])
        return max(1.0, min(5.0, avg_dist * 1.5))

    def cluster_obstacles(self, points: List[Dict]) -> List[List[List[float]]]:
        """DBSCAN으로 장애물 클러스터링."""
        if not points:
            return []
        try:
            coords = [[p['position']['x'], p['position']['z']] for p in points]
            coords = np.array(coords)
            
            with SHARED_LOCK:
                eps = self._adjust_eps(coords)
                min_samples = self.min_samples
            
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