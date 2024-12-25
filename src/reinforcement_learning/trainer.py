from reinforcement_learning.ets2_rl_environment import ETS2RLEnvironment
from stable_baselines3 import PPO

def save_model(model):
    model.save("models/ppo_ets2")

def load_model():
    return PPO.load("models/ppo_ets2")

if __name__ == "__main__":
    env = ETS2RLEnvironment()
    print("ETS2RLEnvironment Loaded, starting the training process")
    model = PPO("MultiInputPolicy", env, verbose=1)
    model.learn(total_timesteps=100)
    model.save("ppo_ets2")