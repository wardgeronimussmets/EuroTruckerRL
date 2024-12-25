import gymnasium as gym
import numpy as np
from reinforcement_learning.step_interpreter import StepInterpreter
from reinforcement_learning.ets2_interactor import ETS2Interactor
import math
import time
import stable_baselines3.common.env_checker

TRUCK_MAX_DETECTABLED_SPEED = 200
MAX_TIME_WITHOUT_PROGRESS_SECONDS = 60

class ETS2RLEnvironment(gym.Env):

    def __init__(self):
        super().__init__()

        '''action space:
            0: throttle application: 0 - accelerate, 1 - coast, 2 - brake
            1: gear control: 0 - downshift, 1 - don't shift, 2 - upshift
            2: steering application: 0 - left, 1 - straight, 2 - right
            3: indicators: 0 - indicate left, 1 - don't indicate, 2 - indicate right
        '''
        self.action_space = gym.spaces.MultiDiscrete([3, 3, 3, 3])

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
                "max_speed": gym.spaces.Box(low=0, high=TRUCK_MAX_DETECTABLED_SPEED, shape=(1,), dtype=np.uint8) #assuming a max speed
            }

        )
        
        self.step_interpreter = StepInterpreter()
        self.ets2_interactor = ETS2Interactor()
        self.current_time_to_travel = 0
        self.last_improvement_time = math.inf

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
        
        
        current_time_to_travel, max_speed, current_speed, info_title, penalty_score, whole_screen_resized = self.step_interpreter.calculate_values()
        positive_reward_score = self.step_interpreter.calculate_reward_score(self.current_time_to_travel, current_time_to_travel, current_speed)
        self.current_time_to_travel = current_time_to_travel
        reward = positive_reward_score - penalty_score
        terminated = False #todo wsme: detect when the job is done
        truncated = self._should_time_out_and_calculate(current_time_to_travel) #when the job takes too long -> time out
        return (self._get_obs(whole_screen_resized, self._rescale_max_speed_if_necesarry(max_speed)), 
                reward, terminated, truncated, 
                self._get_info(
                    current_time_to_travel=current_time_to_travel,
                    max_speed=max_speed,
                    current_speed=current_speed,
                    info_title=info_title,
                    reward_score=reward,
                    whole_screen_resized=whole_screen_resized
                ))
    
    def _rescale_max_speed_if_necesarry(self, max_speed):
        if max_speed > TRUCK_MAX_DETECTABLED_SPEED:
            return TRUCK_MAX_DETECTABLED_SPEED
        return max_speed
    
    def _get_obs(self, screenshot, max_speed):
        return {
            "screen": screenshot,
            "max_speed": max_speed
        }
    
    def _should_time_out_and_calculate(self, current_time_to_travel):
        current_time = time.time()
        if self.current_time_to_travel - current_time_to_travel > 0:
            #making progress
            self.last_improvement_time = current_time
            return False
        else:
            #no progress
            if current_time - self.last_improvement_time > MAX_TIME_WITHOUT_PROGRESS_SECONDS:
                return True
            

    def reset(self, seed=None, options=None):
        self.ets2_interactor.start_new_job()
        current_time_to_travel, max_speed, current_speed, info_title, penalty_score, whole_screen_resized = self.step_interpreter.calculate_values()
        self.current_time_to_travel = current_time_to_travel
        return (self._get_obs(whole_screen_resized, self._rescale_max_speed_if_necesarry(max_speed)), 
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
    stable_baselines3.common.env_checker.check_env(ETS2RLEnvironment(), warn=True, skip_render_check=True)