import cv2
import random
import os

def extract_random_frames(video_path, num_frames, output_folder):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video is opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    # Get total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Make the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generate random frame indices
    frame_indices = random.sample(range(0, total_frames), num_frames)
    
    # Process and capture frames
    for i, frame_index in enumerate(frame_indices):
        # Set the frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        # Read the frame
        ret, frame = cap.read()
        
        if ret:
            # Generate the filename for the screenshot
            output_filename = os.path.join(output_folder, f"frame_{frame_index}.png")
            
            # Save the screenshot
            cv2.imwrite(output_filename, frame)
            print(f"Saved screenshot {output_filename}")
        else:
            print(f"Error reading frame {frame_index}")
    
    # Release the video capture object
    cap.release()

# Usage example:
video_path = "resources/video_footage/2024-12-10 22-20-44.mkv"  # Replace with your video file path
output_folder = "resources/chopped_footage"  # Folder to save screenshots
num_frames = 50  # Number of random frames to capture

extract_random_frames(video_path, num_frames, output_folder)
