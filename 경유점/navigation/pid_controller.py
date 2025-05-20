import time
from config.shared_config import SHARED

class PIDController:
    def __init__(self):
        self.integral_error = 0.0
        self.last_error = 0.0
        self.last_speed_update_time = time.time()
        self.prev_speed_ms = 0.0

    def reset_integral(self):
        """적분항 초기화."""
        self.integral_error = 0.0
        self.last_error = 0.0

    def compute_speed(self, current_speed_kh):
        """PID 제어를 사용하여 속도 계산."""
        target_val_kh = SHARED['tank_tar_val_kh']
        kp_val = SHARED['pid']['kp']
        ki_val = SHARED['pid']['ki']
        kd_val = SHARED['pid']['kd']
        integral_limit = 10.0
        speed_smoothing = 0.7

        error_kh = target_val_kh - current_speed_kh
        now = time.time()
        dt = now - self.last_speed_update_time if now > self.last_speed_update_time else 0.01
        self.last_speed_update_time = now

        self.integral_error += error_kh * dt
        self.integral_error = max(min(self.integral_error, integral_limit), -integral_limit)

        derivative = (error_kh - self.last_error) / dt
        self.last_error = error_kh

        controller_output = kp_val * error_kh + ki_val * self.integral_error + kd_val * derivative
        speed_ms = controller_output / 3.6
        speed_ms = max(min(speed_ms, 70.0 / 3.6), -30.0 / 3.6)
        speed_ms = speed_smoothing * self.prev_speed_ms + (1 - speed_smoothing) * speed_ms
        self.prev_speed_ms = speed_ms
        print(f"PID output: {speed_ms*3.6} km/h, Error: {error_kh}")
        return speed_ms