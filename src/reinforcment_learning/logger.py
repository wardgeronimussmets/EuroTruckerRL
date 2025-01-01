import cv2
import numpy as np
from datetime import datetime
from reinforcment_learning.terminal import TerminalColors, print_colored

LOG_EVERY_N_STEPS = 1000

class StepLogger:
    def __init__(self):
        self.log_counter = LOG_EVERY_N_STEPS + 1
    
    def should_log(self):
        if self.log_counter > LOG_EVERY_N_STEPS:
            self.log_counter = 0
            return True
        else:
            self.log_counter += 1
            return False
    
    def log_data(self, data):
        # print(data)
        create_combined_image(data)
    
def create_combined_image(data_dict):
    # Convert arrays from (channel, height, width) to (height, width, channel)
    current_screen = np.transpose(data_dict['current_screen'], (1, 2, 0))
    current_screen = cv2.cvtColor(current_screen, cv2.COLOR_BGR2RGB)
    previous_screen = np.transpose(data_dict['previous_screen'], (1, 2, 0))
    previous_screen = cv2.cvtColor(previous_screen, cv2.COLOR_BGR2RGB)
    gps_region = np.transpose(data_dict['gps_region'], (1, 2, 0))
    gps_region = cv2.cvtColor(gps_region, cv2.COLOR_BGR2RGB)
    
    # Get the dimensions
    height, width = current_screen.shape[:2]
    
    # Create a larger canvas to hold all images and text
    canvas_height = height * 2 + 60  # Extra space for text
    canvas_width = width * 2
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
    
    # Place current_screen in top-left
    canvas[0:height, 0:width] = current_screen
    
    # Place previous_screen in top-right
    canvas[0:height, width:width*2] = previous_screen
    
    # Place gps_region in bottom-left, scaling to match if dimensions differ
    gps_scaled = cv2.resize(gps_region, (width, height))
    canvas[height:height*2, 0:width] = gps_scaled
    
    # Create a white background for metadata in bottom-right
    canvas[height:height*2, width:width*2] = 255
    
    # Add text for metadata
    metadata_section = canvas[height:height*2, width:width*2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_color = (0, 0, 0)  # Black text
    thickness = 2
    
    # Add metadata text
    metadata_text = [
        f"Current Speed: {data_dict['current_speed']}",
        f"Max Speed: {data_dict['max_speed']}",
        f"Current Gear: {data_dict['current_gear']}"
    ]
    
    y_offset = 40
    for text in metadata_text:
        cv2.putText(metadata_section, text, (20, y_offset), 
                   font, font_scale, font_color, thickness)
        y_offset += 40
    
    # Add labels for each quadrant
    labels = ["Current Screen", "Previous Screen", "GPS Region", "Metadata"]
    positions = [(10, 20), (width+10, 20), (10, height+20), (width+10, height+20)]
    
    for label, pos in zip(labels, positions):
        cv2.putText(canvas, label, pos, font, font_scale, (255, 255, 255), thickness)
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_filename = f"reinforcment_learning/logging/step_logging-{timestamp}.png"
        
    cv2.imwrite(output_filename, canvas)
    print_colored("Saved debug information image to " + output_filename, TerminalColors.INFO)
    return canvas