import time
import my_globals
from pyscript import document, window, when
import js

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

class BallBalancer:
    def __init__(self, path):
        self.path = path
        self.current_target = 0
        self.pid_x = PIDController(kp=1, ki=0.1, kd=0.05)
        self.pid_y = PIDController(kp=1, ki=0.1, kd=0.05)

    def get_ball_position(self):
        return my_globals.x, my_globals.y

    def move_to_next_square(self):
        while self.current_target < len(self.path):
            target = self.path[self.current_target]
            target_x, target_y = map(int, target.split(','))

            reached_target = False
            attempts = 0
            max_attempts = 100

            while not reached_target and attempts < max_attempts:
                ball_x, ball_y = self.get_ball_position()
                
                error_x = target_x - ball_x
                error_y = target_y - ball_y

                if abs(error_x) < 0.1 and abs(error_y) < 0.1:
                    reached_target = True
                    break  # Ball is centered in the target square

                dt = 0.1  # Time step, adjust as needed
                output_x = self.pid_x.compute(error_x, dt)
                output_y = self.pid_y.compute(error_y, dt)

                # Convert PID outputs to motor commands
                motor_b_command = int(output_x)  # Scale as needed
                motor_c_command = int(output_y)  # Scale as needed

                # send commands to Spike Prime
                my_globals.ble.write(f"{motor_b_command}**{motor_c_command})")
                print("SENT: ", motor_b_command, " ", motor_c_command)

                time.sleep(dt)
                attempts += 1

            if reached_target:
                print(f"Reached target {self.current_target + 1} of {len(self.path)}")
                self.current_target += 1
            else:
                print(f"Failed to reach target {self.current_target + 1} after {max_attempts} attempts")
                break  #exit the method if we fail to reach a target

        if self.current_target == len(self.path):
            print("Reached the final destination!")
        else:
            print("Path following incomplete")

    def run(self):
        for _ in range(len(self.path)):
            self.move_to_next_square()
            self.current_target += 1
            if self.current_target >= len(self.path):
                break

def runSpikeToEndPos():
    optimal_path = list(js.window.path) # Use the path generated by pathCalc.js
    balancer = BallBalancer(optimal_path)
    # balancer.run()

window.runSpikeToEndPos = runSpikeToEndPos