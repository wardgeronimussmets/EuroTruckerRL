import pyautogui
import cv2
import numpy as np
from config.config_loader import load_relative_regions_config
import pytesseract
import time
import os
from reinforcment_learning.image_comparer import GearImagePostProcessor

def capture_partial_screen_and_save(relative_region, output_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

    """
    Captures a screenshot of a specific part of the screen and saves it to the specified output path.
    The region is specified as relative values (percentage of the screen width/height).

    Args:
    - relative_region (tuple): A tuple (x_percent, y_percent, width_percent, height_percent)
      where each value is between 0 and 1, representing the percentage of the screen size.
    - output_path (str): The file path where the screenshot will be saved.
    """
    # Get the screen size
    screen_width, screen_height = pyautogui.size()
    
    # Convert relative percentages to absolute pixel values
    x = int(relative_region[0] * screen_width)
    y = int(relative_region[1] * screen_height)
    width = int(relative_region[2] * screen_width)
    height = int(relative_region[3] * screen_height)
    
    # Capture the screen region specified by the 'region' tuple (in absolute pixels)
    start_time = time.time()
    screenshot = pyautogui.screenshot(region=(x, y, width, height)).convert("RGB")
    processed_screenshot = GearImagePostProcessor().process_gear_image(screenshot)
    print(pytesseract.image_to_string(image=screenshot, config='--psm 6'))

    print("Time elapsed:", time.time() - start_time, "s")

    
    # Convert the screenshot to a NumPy array (from PIL Image to OpenCV format)
    screenshot_np = np.array(screenshot)
    
    # Convert RGB to BGR (OpenCV uses BGR by default)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Display the image using OpenCV
    cv2.imshow("Captured Region", processed_screenshot)
    
    # Wait for a key press to close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save the image to the specified path
    cv2.imwrite(output_path, screenshot_bgr)
    print(f"Screenshot saved to: {output_path}")



# Example usage:
# Define the region in relative percentages (from 0 to 1)
relative_region = load_relative_regions_config('lhd_current_gear_region')  # Load region config
output_path = os.path.join(os.getcwd(), "captured_region.png")  # Save to the current working directory

# Capture and save the partial screenshot
capture_partial_screen_and_save(relative_region, output_path)
