import pyautogui
from config.config_loader import load_relative_regions_config
import numpy as np
import cv2

class ScreenGrabber():
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.load_in_ets2_regions()

    def crop_region(self, region, screenshot):
        x = int(region[0] * self.screen_width)
        y = int(region[1] * self.screen_height)
        width = int(region[2] * self.screen_width)
        height = int(region[3] * self.screen_height)
        return screenshot[x:x+width, y:y+height]
    
    def grab_regions(self, regions):
        screenshot = pyautogui.screenshot()
        # Convert the screenshot to a NumPy array (from PIL Image to OpenCV format)
        screenshot_np = np.array(screenshot)
    
        # Convert RGB to BGR (OpenCV uses BGR by default)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        cropped_images = []
        for region in regions:
            cropped_images.append(self.crop_region(region, screenshot_bgr))
        return cropped_images
    
    def load_in_ets2_regions(self):
        self.regions = [load_relative_regions_config('information_region'), 
                        load_relative_regions_config('max_speed_region'),
                        load_relative_regions_config('current_speed_region')]
        
    def get_regions(self):
        return self.grab_regions(self.regions)
        