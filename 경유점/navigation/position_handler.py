import math
import time
from config.shared_config import SHARED

class PositionHandler:
    def __init__(self):
        self.current_position = None
        self.current_heading = 0.0
        self.current_speed_kh = 0.0
        self.smoothed_speed_kh = 0.0
        self.last_update_time = time.time()

    def update_position(self, position_str):
        """새 위치 데이터를 기반으로 현재 위치, 방향, 속도를 업데이트."""
        try:
            now = time.time()
            dt = now - self.last_update_time if now > self.last_update_time else 0.01
            dt = max(dt, 0.01)
            self.last_update_time = now

            x, y, z = map(float, position_str.split(","))
            new_position = (x, z)

            if self.current_position:
                prev_x, prev_z = self.current_position
                dx = x - prev_x
                dz = z - prev_z

                # 위치 변화량 저장
                SHARED['del_playerPos_x'].append(dx)
                SHARED['del_playerPos_z'].append(dz)
                if len(SHARED['del_playerPos_x']) > 1000:
                    SHARED['del_playerPos_x'] = SHARED['del_playerPos_x'][-1000:]
                    SHARED['del_playerPos_z'] = SHARED['del_playerPos_z'][-1000:]
                print(f"Delta position appended: dX={dx}, dZ={dz}")

                distance_moved = math.sqrt(dx**2 + dz**2)
                if distance_moved > 0.01:
                    new_heading = math.atan2(dx, dz)
                    self.current_heading = (
                        SHARED['CONFIG_PARAMS']['HEADING_SMOOTHING'] * self.current_heading +
                        (1 - SHARED['CONFIG_PARAMS']['HEADING_SMOOTHING']) * new_heading
                    )
                    self.current_heading = math.atan2(
                        math.sin(self.current_heading), math.cos(self.current_heading)
                    )
                    if dt > 0:
                        max_distance = (abs(SHARED['tank_tar_val_kh']) / 3.6) * dt
                        distance_moved = min(distance_moved, max_distance)
                        raw_speed_kh = (distance_moved / dt) * 3.6
                        raw_speed_kh = min(raw_speed_kh, abs(SHARED['tank_tar_val_kh']))
                        if SHARED['tank_tar_val_kh'] < 0:
                            raw_speed_kh = -raw_speed_kh
                        smoothing = 0.7
                        self.smoothed_speed_kh = (
                            smoothing * self.smoothed_speed_kh +
                            (1 - smoothing) * raw_speed_kh
                        )
                        self.smoothed_speed_kh = max(min(self.smoothed_speed_kh, 70.0), -30.0)
                        self.current_speed_kh = self.smoothed_speed_kh

                        # 속도 데이터 저장
                        SHARED['speed_data'].append(self.current_speed_kh)
                        print(f"Speed data appended: {self.current_speed_kh}, Total points: {len(SHARED['speed_data'])}")
                        if len(SHARED['speed_data']) > 1000:
                            SHARED['speed_data'] = SHARED['speed_data'][-1000:]

            # 전차 위치 저장
            SHARED['player_pos'].append(new_position)
            if len(SHARED['player_pos']) > 1000:
                SHARED['player_pos'] = SHARED['player_pos'][-1000:]
            print(f"Position appended: {new_position}")

            self.current_position = new_position
            print(f"Position updated: {self.current_position}, Heading: {math.degrees(self.current_heading)}")
            return {
                "status": "OK",
                "current_position": self.current_position,
                "heading": math.degrees(self.current_heading),
                "speed_kh": self.current_speed_kh
            }
        except Exception as e:
            print(f"Error in update_position: {str(e)}")
            return {"status": "ERROR", "message": str(e)}