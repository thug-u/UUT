import math
import random
import numpy as np
from config.shared_config import SHARED

class PurePursuit:
    def __init__(self):
        self.last_command = None
        self.last_steering = 0.0
        self.initial_distance = None

    def compute_move(self, current_position, current_heading, current_speed_kh, destination, controller, obstacle_handler):
        """Pure Pursuit 알고리즘으로 이동 명령 계산."""
        if current_position is None or destination is None:
            print("No movement: Position or destination is None")
            return {"move": "STOP", "weight": 1.0}

        curr_x, curr_z = current_position
        dest_x, dest_z = destination
        distance = math.sqrt((dest_x - curr_x) ** 2 + (dest_z - curr_z) ** 2)
        print(f"Distance to destination: {distance}")

        if distance < SHARED['CONFIG_PARAMS']['TOLERANCE']:
            self.initial_distance = None
            controller.reset_integral()
            print("Destination reached, stopping")
            return {"move": "STOP", "weight": 1.0}

        lookahead_distance = min(
            SHARED['CONFIG_PARAMS']['LOOKAHEAD_MAX'],
            max(SHARED['CONFIG_PARAMS']['LOOKAHEAD_MIN'], distance * 0.5)
        )
        goal_vector = np.array([dest_x - curr_x, dest_z - curr_z])
        goal_distance = np.linalg.norm(goal_vector)

        if goal_distance > 0:
            goal_vector = goal_vector / goal_distance

        target_vector = goal_vector * SHARED['CONFIG_PARAMS']['GOAL_WEIGHT']
        target_vector_norm = np.linalg.norm(target_vector)

        if target_vector_norm > 0:
            target_vector = target_vector / target_vector_norm
            target_heading = math.atan2(target_vector[0], target_vector[1])
        else:
            target_heading = math.atan2(goal_vector[0], goal_vector[1])

        lookahead_x = curr_x + target_vector[0] * lookahead_distance
        lookahead_z = curr_z + target_vector[1] * lookahead_distance

        if obstacle_handler.is_obstacle_in_path(curr_x, curr_z, lookahead_x, lookahead_z):
            print("Obstacle detected, stopping")
            return {"move": "STOP", "weight": 1.0, "message": "Obstacle detected in path"}

        dx = lookahead_x - curr_x
        dz = lookahead_z - curr_z
        target_heading = math.degrees(math.atan2(dx, dz))
        steering = target_heading - math.degrees(current_heading)
        steering = ((steering + 180) % 360) - 180
        # 조향 평활화 적용
        steering = (
            SHARED['CONFIG_PARAMS']['STEERING_SMOOTHING'] * self.last_steering +
            (1 - SHARED['CONFIG_PARAMS']['STEERING_SMOOTHING']) * steering
        )
        self.last_steering = steering
        print(f"Steering calculated: {steering}, Target heading: {target_heading}")

        speed_ms = controller.compute_speed(current_speed_kh)
        abs_steering = abs(steering / 180.0)
        speed_ms = speed_ms * (1.0 - abs_steering * SHARED['CONFIG_PARAMS']['SPEED_FACTOR'])
        speed_ms = max(min(speed_ms, 70.0 / 3.6), -30.0 / 3.6)
        print(f"Speed calculated: {speed_ms*3.6} km/h, Target speed: {SHARED['tank_tar_val_kh']}")

        progress = max(0, 1 - distance / self.initial_distance) if self.initial_distance and distance > 0 else 0.0

        dynamic_weights = {
            "D": SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['D'] * (1 + abs_steering * 0.01) if steering > 0 else 0.0,
            "A": SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['A'] * (1 + abs_steering * 0.01) if steering < 0 else 0.0,
            "W": SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['W'] * abs(speed_ms) if speed_ms > 0 else 0.0,
            "S": SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['S'] * abs(speed_ms) if speed_ms < 0 else 0.0
        }
        print(f"Dynamic weights: {dynamic_weights}")

        for cmd in dynamic_weights:
            if dynamic_weights[cmd] > 0:
                dynamic_weights[cmd] *= (1 + progress * 0.5)

        commands = [cmd for cmd, w in dynamic_weights.items() if w > 0]
        if not commands:
            command = {"move": "STOP"}
        else:
            weights = [dynamic_weights[cmd] for cmd in commands]
            chosen_cmd = random.choices(commands, weights=weights, k=1)[0]
            command = {"move": chosen_cmd, "weight": dynamic_weights[chosen_cmd]}
            self.last_command = chosen_cmd
        print(f"Command chosen: {command}")

        if self.last_command:
            move_distance = SHARED['CONFIG_PARAMS']['MOVE_STEP'] * abs(speed_ms)
            new_x, new_z = curr_x, curr_z

            if self.last_command == "D":
                new_x += move_distance * math.cos(current_heading + math.pi/2)
                new_z += move_distance * math.sin(current_heading + math.pi/2)
            elif self.last_command == "A":
                new_x += move_distance * math.cos(current_heading - math.pi/2)
                new_z += move_distance * math.sin(current_heading - math.pi/2)
            elif self.last_command == "W":
                new_x += move_distance * math.sin(current_heading) * (1 if speed_ms > 0 else -1)
                new_z += move_distance * math.cos(current_heading) * (1 if speed_ms > 0 else -1)
            elif self.last_command == "S":
                new_x -= move_distance * math.sin(current_heading) * (1 if speed_ms > 0 else -1)
                new_z -= move_distance * math.cos(current_heading) * (1 if speed_ms > 0 else -1)

            print(f"New position calculated: ({new_x}, {new_z})")
            return command, (new_x, new_z)
        return command, None