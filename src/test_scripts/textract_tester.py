import pyautogui
import cv2
import numpy as np
from config.config_loader import load_relative_regions_config

def capture_partial_screen_and_display(relative_region):
    """
    Captures a screenshot of a specific part of the screen and displays it using OpenCV.
    The region is specified as relative values (percentage of the screen width/height).

    Args:
    - relative_region (tuple): A tuple (x_percent, y_percent, width_percent, height_percent)
      where each value is between 0 and 1, representing the percentage of the screen size.
    """
    # Get the screen size
    screen_width, screen_height = pyautogui.size()
    
    # Convert relative percentages to absolute pixel values
    x = int(relative_region[0] * screen_width)
    y = int(relative_region[1] * screen_height)
    width = int(relative_region[2] * screen_width)
    height = int(relative_region[3] * screen_height)
    
    # Capture the screen region specified by the 'region' tuple (in absolute pixels)
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    # Convert the screenshot to a NumPy array (from PIL Image to OpenCV format)
    screenshot_np = np.array(screenshot)
    
    # Convert RGB to BGR (OpenCV uses BGR by default)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Display the image using OpenCV
    cv2.imshow("Captured Region", screenshot_bgr)
    
    # Wait for a key press to close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage:
# Define the region in relative percentages (from 0 to 1)
# Example: (0.1, 0.1, 0.5, 0.5) will capture a 50% width and 50% height starting at (10%, 10%) of the screen.
relative_region = load_relative_regions_config('max_speed_region')  # 10% from the top-left corner, 50% width, 50% height

# Capture and display the partial screenshot
capture_partial_screen_and_display(relative_region)
