import pyautogui
from config.config_loader import load_relative_regions_config
from reinforcement_learning.types import RightLeftHandDriveType
import numpy as np
import cv2

class ScreenGrabber():
    def __init__(self, training_screen_size=(240, 134), left_right_hand_drive_type=RightLeftHandDriveType.NONE):
        self.training_screen_size = training_screen_size
        self.screen_width, self.screen_height = pyautogui.size()
        self.left_right_hand_drive_type = left_right_hand_drive_type
        self._load_in_ets2_regions(ignore_warnings=True)

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

    
    def _grab_region_images_and_whole(self, regions):
        screenshot = np.array(pyautogui.screenshot().convert("RGB"))
        cropped_images = []
        for i, region in enumerate(regions):
            cropped_images.append(self._crop_region(region, screenshot))
        #add the whole screenshot
        cropped_images.append(cv2.resize(screenshot, self.training_screen_size, interpolation=cv2.INTER_LINEAR))
        return cropped_images
    
    def _load_in_ets2_regions(self, ignore_warnings=False):
        if self.left_right_hand_drive_type == RightLeftHandDriveType.RIGHT:
            self.regions = [
                load_relative_regions_config('rhd_information_region'), 
                load_relative_regions_config('rhd_max_speed_region'),
                load_relative_regions_config('rhd_current_speed_region'),
                load_relative_regions_config('rhd_text_information_region'),
                load_relative_regions_config('rhd_additional_info_region')
            ]
            return
        elif self.left_right_hand_drive_type == RightLeftHandDriveType.NONE and not ignore_warnings:
            print("Warning: left_right_hand_drive_type is not set, defaulting to LeftHandDrive")
        self.regions = [
            load_relative_regions_config('lhd_information_region'), 
            load_relative_regions_config('lhd_max_speed_region'),
            load_relative_regions_config('lhd_current_speed_region'),
            load_relative_regions_config('lhd_text_information_region'),
            load_relative_regions_config('lhd_additional_info_region')
        ]

    def get_current_time_to_travel_image_index(self):
        return 0
    
    def get_max_speed_image_index(self):
        return 1
    
    def get_current_speed_image_index(self):
        return 2
    
    def get_info_title_image_index(self):
        return 3
    
    def get_gps_info_image_index(self):
        return 4
    
    def get_whole_screen_resized_image_index(self):
        return 5
        
    #returns information_region, max_speed_region, current_speed_region
    def get_images(self):
        return self._grab_region_images_and_whole(self.regions)
    
    def get_cursor_on_drive_region(self):
        return self._crop_region(load_relative_regions_config('cursor_on_drive_region'), np.array(pyautogui.screenshot().convert("RGB")))
    