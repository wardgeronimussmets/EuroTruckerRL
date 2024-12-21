import pyautogui
from config.config_loader import load_relative_regions_config
import numpy as np
from PIL import Image

class ScreenGrabber():
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self._load_in_ets2_regions()

    def _crop_region(self, region, screenshot):
        x = int(region[0] * self.screen_width)  # Starting x (column)
        y = int(region[1] * self.screen_height)  # Starting y (row)
        width = int(region[2] * self.screen_width)  # Width of region
        height = int(region[3] * self.screen_height)  # Height of region

         # Validate cropping dimensions
        if not (0 <= x < self.screen_width and 0 <= y < self.screen_height):
            raise ValueError("Crop start points are outside the image bounds.")
        if not (x + width <= self.screen_width and y + height <= self.screen_height):
            raise ValueError("Crop dimensions extend outside the image.")
        
        # Proper NumPy slicing: [rows (height), columns (width)]
        return screenshot[y:y+height, x:x+width]

    
    def _grab_regions(self, regions):
        screenshot = np.array(pyautogui.screenshot().convert("RGB"))
        cropped_images = []
        for i, region in enumerate(regions):
            cropped_images.append(self._crop_region(region, screenshot))
        return cropped_images
    
    def _load_in_ets2_regions(self):
        self.regions = [load_relative_regions_config('information_region'), 
                        load_relative_regions_config('max_speed_region'),
                        load_relative_regions_config('current_speed_region'),
                        load_relative_regions_config('text_information_region'),
                        load_relative_regions_config('additional_info_region')]
        
    #returns information_region, max_speed_region, current_speed_region
    def get_regions(self):
        return self._grab_regions(self.regions)
