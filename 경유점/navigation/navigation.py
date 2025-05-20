import math
from navigation.position_handler import PositionHandler
from navigation.pid_controller import PIDController
from navigation.purepursuit import PurePursuit
from navigation.obstacle_handler import ObstacleHandler  # 수정됨

class Navigation:
    def __init__(self):
        self.position_handler = PositionHandler()
        self.controller = PIDController()
        self.pure_pursuit = PurePursuit()
        self.obstacle_handler = ObstacleHandler()  # 수정됨
        self.enemyPos = None                       # 추가
        self.destination = None
        self.start_mode = "start"

    def init_simulation(self):
        """시뮬레이션 초기화."""
        self.position_handler = PositionHandler()
        self.controller = PIDController()
        self.pure_pursuit = PurePursuit()
        self.obstacle_handler = ObstacleHandler()
        self.destination = None
        self.start_mode = "start"
        return {"status": "OK", "message": "Simulation initialized"}

    def set_destination(self, destination_str):
        """목적지를 설정하고 초기 거리를 계산."""
        try:
            x, y, z = map(float, destination_str.split(","))
            self.destination = (x, z)
            self.controller.reset_integral()
            self.pure_pursuit.initial_distance = None

            if self.position_handler.current_position:
                curr_x, curr_z = self.position_handler.current_position
                self.pure_pursuit.initial_distance = math.sqrt((x - curr_x) ** 2 + (z - curr_z) ** 2)

            return {
                "status": "OK",
                "destination": {"x": x, "y": y, "z": z},
                "initial_distance": self.pure_pursuit.initial_distance
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
        
    def update_info(self, data):
        """LiDAR 데이터와 플레이어 위치 데이터를 처리."""
        try:
            # print(f"Received /info data: {data}")
            # if "lidarPoints" not in data:
            #     return {"status": "ERROR", "message": "No lidarPoints in data"}
            
            # # LiDAR 데이터 처리
            # obstacle_result = self.obstacle_handler.update_obstacle({"lidarPoints": data["lidarPoints"]})
            # if obstacle_result["status"] == "ERROR":
            #     return obstacle_result

            # 플레이어 위치 데이터 처리 _ 지혁 사용
            if "playerPos" in data and isinstance(data["playerPos"], dict):
                position_str = f"{data['playerPos']['x']},{data['playerPos']['y']},{data['playerPos']['z']}"
                position_result = self.position_handler.update_position(position_str)
                if position_result["status"] == "ERROR":
                    return position_result
            # print("지혁지혁혁- 우리좌표-str",position_str)    
            
            # 2. 적 위치 -- 위와 동시에 경로 짜기기 
            if "enemyPos" in data and isinstance(data["enemyPos"], dict):
                self.enemyPos = (
                    data["enemyPos"]["x"],
                    # data["enemyPos"]["y"], 
                    data["enemyPos"]["z"]
                )
            # print('~적좌표 ~ 적좌표 ~',data["enemyPos"]["x"], data["enemyPos"]["z"])

            # 3. 플레이어 터렛 방향
            # if "player_turret_x" in data:
            #     self.player_turret_x = data["player_turret_x"]

            # 4. 적 터렛 방향
            if "enemyTurretX" in data:
                self.enemyTurretX = data["enemyTurretX"]


            # # 5. 플레이어 몸체 자세 (IMU-like 값)
            # self.player_body_attitude = {
            #     "x": data.get("playerBodyX", 0),
            #     "y": data.get("playerBodyY", 0),
            #     "z": data.get("playerBodyZ", 0)
            # }

            # 1. 적 포신 radian으로 변환
            theta = math.radians(self.enemyTurretX)
            # print(f"[DEBUG1] 적 터렛 각도 (도): {self.enemyTurretX}, (라디안): {theta:.4f}")

            # 2. 적 포신 방향벡터 (항법 좌표계 -> xy좌표계)
            dx = math.sin(theta)
            dz = math.cos(theta)
            # print(f"[DEBUG2] 적의 방향벡터: dx = {dx:.4f}, dz = {dz:.4f}")

            # 3. 직선 위의 점 (적 위치)
            x0 = data['enemyPos']['x']
            z0 = data['enemyPos']['z']
            # print(f"[DEBUG3] 적 위치: x0 = {x0}, z0 = {z0}")

            # 4. 외부 점 (플레이어 위치)
            x1 = data['playerPos']['x']
            z1 = data['playerPos']['z']
            # print(f"[DEBUG4] 플레이어 위치: x1 = {x1}, z1 = {z1}")

            # 수선의 발 : 최단거리로 가기위한 경유점
            denominator = dx**2 + dz**2
            if denominator == 0:
                raise ValueError("dx and dz cannot both be zero")
    
            self.x2 = (dx**2 * x0 + dz**2 * x1 + dx * dz * (z0 - z1)) / denominator
            self.z2 = (dz**2 * z0 + dx**2 * z1 + dx * dz * (x0 - x1)) / denominator

            print("수선의 발발발5~~",self.x2, self.z2)
            
            # 최종 지점 : 100m 지점
            d = math.sqrt((self.x2 - x0)**2 + (self.z2 - z0)**2)
            if d <= 10:
                raise ValueError("ㅠㅠㅠ 점(x2, z2) must be outside the circle (distance > 10 (단위모르니~)") 
            
            self.x3 = x0 + (100 / d) * (self.x2 - x0)
            self.z3 = z0 + (100 / d) * (self.z2 - z0)
            print("100m 지점점점점~~", self.x3, self.z3)

            return {"status": "OK"}

        except Exception as e:
            print(f"Error in update_info: {str(e)}")
            return {"status": "ERROR", "message": f"Failed to update info: {str(e)}"}
 
    # def update_obstacle(self, obstacle_data):
    #     """장애물 데이터 업데이트."""
    #     return self.obstacle_handler.update_obstacle(obstacle_data)
    

    def get_move(self):
        """장애물 회피 여부를 먼저 판단하고, Pure Pursuit로 이동 명령 계산."""
        if self.start_mode == "pause":
            return {"move": "STOP", "weight": 1.0}

        # --- 장애물 회피 우선 판단 ---
        avoidance_command = self.obstacle_handler.get_avoidance_command(
            self.position_handler.current_position,
            self.position_handler.current_heading
        )
        if avoidance_command:
            return avoidance_command

        # --- 장애물 없으면 순수 주행 ---
        command, new_position = self.pure_pursuit.compute_move(
            self.position_handler.current_position,
            self.position_handler.current_heading,
            self.position_handler.current_speed_kh,
            self.destination,
            self.controller,
            self.obstacle_handler
        )

        if new_position:
            self.position_handler.current_position = new_position

        return command
