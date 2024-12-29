import gymnasium as gym
import numpy as np
from reinforcement_learning.step_interpreter import StepInterpreter
from reinforcement_learning.ets2_interactor import ETS2Interactor
from reinforcement_learning.terminal import TerminalColors
import math
import time
import stable_baselines3.common.env_checker

TRUCK_MAX_DETECTABLED_SPEED = 200
MAX_TIME_WITHOUT_PROGRESS_SECONDS = 60

class ETS2RLEnvironment(gym.Env):

    def __init__(self, skip_initialize=False):
        super().__init__()

        '''action space:
            0: throttle application: 0 - accelerate, 1 - coast, 2 - brake
            1: gear control: 0 - downshift, 1 - don't shift, 2 - upshift
            2: steering application: 0 - left, 1 - straight, 2 - right
            3: indicators: 0 - indicate left, 1 - don't indicate, 2 - indicate right
            4: lights: 0 - off, 1 - parking mode, 2 - on, 3 - high beams
        '''
        self.action_space = gym.spaces.MultiDiscrete([3, 3, 3, 3, 4])

        # Observation space:        (the screen)
        N_CHANNELS = 3
        HEIGHT = 134
        WIDTH = 240
        ''' observation space:
                screen: "screenshot rezised",
                max_speed: max speed numb
        '''
        self.observation_space = gym.spaces.Dict(
            {
                "screen": gym.spaces.Box(low=0, high=255,
                                                shape=(N_CHANNELS, HEIGHT, WIDTH), dtype=np.uint8),
                "max_speed": gym.spaces.Discrete(TRUCK_MAX_DETECTABLED_SPEED + 1),  # assuming max speed is inclusive
                "current_speed": gym.spaces.Discrete(TRUCK_MAX_DETECTABLED_SPEED + 1),
            }
        )
        
        self.step_interpreter = StepInterpreter()
        self.ets2_interactor = ETS2Interactor(skip_initialize=skip_initialize, log_inputs=False)
        self.previous_time_to_travel = 0
        self.last_improvement_time = math.inf
        
        self.cumulated_reward = 0
        self.cumulated_reward_count = 0
        self.step_count = 0

    def step(self, action):
        if action is None:
            action = np.ones(4, dtype=np.int32)

        throttle_input = action[0]
        match throttle_input:
            case 0:
                self.ets2_interactor.accelerate_full()
            case 1:
                self.ets2_interactor.coast()
            case 2:
                self.ets2_interactor.brake_full()
            
        gearbox_control = action[1]
        match gearbox_control:
            case 0:
                self.ets2_interactor.downshift()
            case 2:
                self.ets2_interactor.upshift()

        steering_input = action[2]
        match steering_input:
            case 0:
                self.ets2_interactor.steer_left_full()
            case 1:
                self.ets2_interactor.steer_straight()
            case 2:
                self.ets2_interactor.steer_right_full()

        indicator_input = action[3]
        match indicator_input:
            case 0:
                self.ets2_interactor.indicate_left()
            case 2:
                self.ets2_interactor.indicate_right()
                
        lights_input = action[4]
        match lights_input:
            case 0:
                self.ets2_interactor.lights_off()
            case 1:
                self.ets2_interactor.lights_parking()
            case 2:
                self.ets2_interactor.lights_on()
            case 3:
                self.ets2_interactor.high_beams()
        
        
        current_time_to_travel_uncleaned, max_speed, current_speed, info_title, unruly_behaviour_score, whole_screen_resized = self.step_interpreter.calculate_values()
        current_time_to_travel = self._clean_time_to_travel(current_time_to_travel_uncleaned)
        position_reward_score = self.step_interpreter.calculate_position_reward_score(self.previous_time_to_travel, current_time_to_travel, current_speed)
        reward = position_reward_score - unruly_behaviour_score
        terminated = False #todo wsme: detect when the job is done
        truncated = self._should_time_out_and_calculate(current_time_to_travel) #when the job takes too long -> time out
        self.previous_time_to_travel = current_time_to_travel
        self._progress_logging(reward)
        return (self._get_obs(whole_screen_resized, self._rescale_speed_if_necesarry(max_speed), self._rescale_speed_if_necesarry(current_speed)), 
                reward, terminated, truncated, 
                self._get_info(
                    current_time_to_travel=current_time_to_travel,
                    max_speed=max_speed,
                    current_speed=current_speed,
                    info_title=info_title,
                    reward_score=reward,
                    whole_screen_resized=whole_screen_resized
                ))
    
    def _progress_logging(self, reward):
        self.cumulated_reward += reward
        self.cumulated_reward_count += 1
        self.step_count += 1
        if self.cumulated_reward_count > 100:
            print("After", self.step_count, "steps, the acumulated reward is:", self.cumulated_reward)
            self.cumulated_reward = 0
            self.cumulated_reward_count = 0

    def _clean_time_to_travel(self, time_to_travel):
        if time_to_travel is None:
            if self.previous_time_to_travel is None:
                return 0
            else:
                return self.previous_time_to_travel
        return time_to_travel
    
    def _rescale_speed_if_necesarry(self, max_speed):
        if max_speed > TRUCK_MAX_DETECTABLED_SPEED:
            return TRUCK_MAX_DETECTABLED_SPEED
        return max_speed
    
    def _get_obs(self, screenshot, max_speed, current_speed):
        return {
            "screen": screenshot,
            "max_speed": max_speed,
            "current_speed": current_speed
        }
    
    def _should_time_out_and_calculate(self, current_time_to_travel):
        current_time = time.time()
        print(f"in time out: current_time_to_travel: {current_time_to_travel}, self.previous_time_to_travel: {self.previous_time_to_travel}")
        if self.previous_time_to_travel - current_time_to_travel > 0:
            #making progress
            self.last_improvement_time = current_time
        else:
            #no progress
            if current_time - self.last_improvement_time > MAX_TIME_WITHOUT_PROGRESS_SECONDS:
                print(f"{TerminalColors.INFO}Timed out, to long ({current_time - self.last_improvement_time}) seconds without progress{TerminalColors.ENDC}")
                return True
        return False
            

    def reset(self, seed=None, options=None):
        self.ets2_interactor.start_new_job()
        self.step_interpreter.set_right_left_hand_drive()
        self.last_improvement_time = time.time()
        current_time_to_travel_uncleaned, max_speed, current_speed, info_title, penalty_score, whole_screen_resized = self.step_interpreter.calculate_values()
        current_time_to_travel = self._clean_time_to_travel(current_time_to_travel_uncleaned)
        self.previous_time_to_travel = current_time_to_travel
        return (self._get_obs(whole_screen_resized, self._rescale_speed_if_necesarry(max_speed), self._rescale_speed_if_necesarry(current_speed)), 
                self._get_info(
                    current_time_to_travel=current_time_to_travel,
                    max_speed=max_speed,
                    current_speed=current_speed,
                    user_logs="Reset the environment"
                ))        
    
    def _get_info(self, **kwargs):
        # Define the list of allowed keys
        allowed_keys = [
            "current_time_to_travel",
            "max_speed",
            "current_speed",
            "info_title",
            "reward_score",
            "whole_screen_resized",
            "user_logs"
        ]
        # Filter out any unexpected or None values
        return {key: value for key, value in kwargs.items() if key in allowed_keys and value is not None}


    def render(self):
        pass

    def close(self):
        pass

if __name__ == "__main__":
    print("Testing environment")
    stable_baselines3.common.env_checker.check_env(ETS2RLEnvironment(skip_initialize=False), warn=True, skip_render_check=True)