from reinforcment_learning.ets2_rl_environment import ETS2RLEnvironment
from stable_baselines3 import PPO
from reinforcment_learning.terminal import TerminalColors, print_colored
from stable_baselines3.common.callbacks import BaseCallback, EveryNTimesteps
import os
from datetime import datetime


def save_model(model):
    save_at_basepath(model, "reinforcment_learning/models")

def load_model(env):
    print_colored("Loading model", TerminalColors.INFO)
    return PPO.load("reinforcment_learning/models/ppo_ets2", env, verbose=2)

def new_model(env):
    return PPO("MultiInputPolicy", env, verbose=2)


class SaveModelCallback(BaseCallback):
    def __init__(self, model, verbose=0):
        super().__init__(verbose)
        self.model = model
    
    def _on_step(self) -> bool:
        save_at_basepath(self.model, "reinforcment_learning/models/checkpoints")        
        return True
    
def save_at_basepath(model, base_path, is_from_checkpoint=False):
    if model is None:
        raise ValueError("Model cannot be None")
    
    check_point_indication_string = "at checkpoint" if is_from_checkpoint else ""    
    print_colored("Saving model " + check_point_indication_string, TerminalColors.INFO)
    
    # Get today's date in 'yyyy_mm_dd' format
    today = datetime.today().strftime('%Y_%m_%d')
    
    # Set the initial file name
    base_filename = f"{base_path}/ppo_ets2_{today}"
    
    # Check if file already exists and increment number if it does
    filename = base_filename
    counter = 1
    while os.path.exists(f"{filename}.zip"):  # Assuming the model is saved as .zip, adjust if needed
        filename = f"{base_filename}_{counter}"
        counter += 1
    
    # Save the model with the appropriate file name
    model.save(f"{filename}")
    print_colored(f"Model at checkpoint saved as {filename}.zip", TerminalColors.INFO)

if __name__ == "__main__":
    env = ETS2RLEnvironment()
    print("ETS2RLEnvironment Loaded, starting the training process")
    model = load_model(env)
    # model = new_model(env)
    
    # Pass the custom callback to EveryNTimesteps
    event_callback = EveryNTimesteps(n_steps=800, callback=SaveModelCallback(model))
    
    # Train the model and invoke the callback
    model.learn(total_timesteps=1000, callback=event_callback)
    
    # Save the final model
    save_model(model)