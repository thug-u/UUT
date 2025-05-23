
import math



class Navigation:
    def __init__(self):
        self.enemyPos = None 

    def update_info(self, data):
        try:
            # 플레이어 위치 데이터 처리 _ 지혁 사용- 그래서 얘만 str임임
            if "playerPos" in data and isinstance(data["playerPos"], dict):
                position_str = f"{data['playerPos']['x']},{data['playerPos']['y']},{data['playerPos']['z']}"
                position_result = self.position_handler.update_position(position_str)
                if position_result["status"] == "ERROR":
                    return position_result
            # print("지혁 내위치 좌표_str",position_str)    
            
            # 적 위치 -- 위와 동시에 경로 짜기
            if "enemyPos" in data and isinstance(data["enemyPos"], dict):
                self.enemyPos = (
                    data["enemyPos"]["x"],
                    # data["enemyPos"]["y"], 
                    data["enemyPos"]["z"]
                )
            # print('~적좌표 ~ 적좌표 ~',data["enemyPos"]["x"], data["enemyPos"]["z"])

            # 적 터렛 방향 - 어짜피 못움직이니 이걸걸 방향이라 간주했음음
            if "enemyTurretX" in data:
                self.enemyTurretX = data["enemyTurretX"]

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

            # 4-1. 상대 시야에 있는지~
            if dx*(x0-x1) + dz*(z0-z1) > 0:
                print("🟢 뒤치 가능")
            else:
                print("🔴 위험해")

            # 5. 수선의 발 : 최단거리로 가기위한 경유점
            denominator = dx**2 + dz**2
            if denominator == 0:
                raise ValueError("dx and dz cannot both be zero")
    
            self.x2 = (dx**2 * x0 + dz**2 * x1 + dx * dz * (z0 - z1)) / denominator
            self.z2 = (dz**2 * z0 + dx**2 * z1 + dx * dz * (x0 - x1)) / denominator

            print("수선의 발발발5~~",self.x2, self.z2)
            
            # 6. 최종 지점 : 100m 지점 , 그 범위가 안되면 ㅠㅠ 출력
            d = math.sqrt((self.x2 - x0)**2 + (self.z2 - z0)**2)
            if d <= 100:
                raise ValueError("ㅠㅠㅠ 수선의발 must be outside the circle (distance > 100") 
            
            self.x3 = x0 + (100 / d) * (self.x2 - x0)
            self.z3 = z0 + (100 / d) * (self.z2 - z0)
            print("100m 지점점점점~~", self.x3, self.z3)

            return {"status": "OK"}

        except Exception as e:
            print(f"Error in update_info: {str(e)}")
            return {"status": "ERROR", "message": f"Failed to update info: {str(e)}"}
 
