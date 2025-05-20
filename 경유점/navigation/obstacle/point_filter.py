import numpy as np
import logging
from typing import List, Dict

logging.basicConfig(level=logging.DEBUG)

class PointFilter:
    """라이다 포인트 필터링을 담당."""
    def filter_points(self, points: List[Dict]) -> List[Dict]:
        """포인트 필터링: 유효한 포인트만 반환."""
        filtered = [
            p for p in points
            if isinstance(p, dict) and 
            isinstance(p.get('position'), dict) and
            'x' in p['position'] and 'z' in p['position'] and
            0.05 < np.sqrt(p['position']['x']**2 + p['position']['z']**2) < 100.0
        ]
        logging.debug(f"Filtered lidar points: {len(filtered)}/{len(points)}")
        return filtered