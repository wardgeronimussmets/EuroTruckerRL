import cv2
import numpy as np
from datetime import datetime

LOG_EVERY_N_STEPS = 100

class StepLogger:
    def __init__(self):
        self.log_counter = LOG_EVERY_N_STEPS
    
    def should_log(self):
        return self.log_counter > LOG_EVERY_N_STEPS
    
    def log_data(self, data):
        self.log_counter = 0
        create_combined_image(data)

def create_combined_image(data):
    """
    Combines images and associated numbers into a single image and saves it to a file.

    Args:
        data (dict): A dictionary where keys are labels (optional), and values are tuples of (image, number).
                     - `image`: The image as a numpy array (readable by OpenCV).
                     - `number`: The associated numeric value to display.
    """
    # Get current datetime for filename
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_filename = f"reinforcment_learning/logging/step_logging-{timestamp}.png"
    
    # Initialize list to store rows for the combined image
    combined_rows = []

    # Define font and spacing parameters for OpenCV text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    padding = 10

    for label, (image, number) in data.items():
        # Add label and number as text
        text = f"{label}: {number}" if label else str(number)
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        # Create a blank canvas for the text
        text_canvas = np.ones((image.shape[0], text_size[0] + 2 * padding, 3), dtype=np.uint8) * 255

        # Put text onto the canvas
        cv2.putText(text_canvas, text, (padding, image.shape[0] // 2 + text_size[1] // 2),
                    font, font_scale, (0, 0, 0), font_thickness)

        # Combine the image and the text canvas side by side
        combined_row = np.hstack((image, text_canvas))
        combined_rows.append(combined_row)

    # Stack all rows vertically
    combined_image = np.vstack(combined_rows)

    # Save the resulting image
    cv2.imwrite(output_filename, combined_image)
