from reinforcment_learning.screen_grabber import ScreenGrabber
from reinforcment_learning.image_comparer import ImageInfoComparer, ImageSimilarityMatch, RightLeftHandDriveComparer, GearImageComparer
from reinforcment_learning.types import RightLeftHandDriveType
from reinforcment_learning.terminal import print_colored, TerminalColors
import pytesseract
import time
import re
import cv2
import numpy as np

INFO_DETECTED_TIMEOUT_SECONDS = 2.5 #Don't detect fines multiple times

class StepInterpreter:
    def __init__(self, training_screen_size=(240, 134)):
        self.screen_grabber = ScreenGrabber(training_screen_size)
        self.image_info_comparer = ImageInfoComparer()
        self.right_left_hand_comparer = RightLeftHandDriveComparer()
        self.last_info_detected_time = 0 #info detection should be time as to not detect it multiple times
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
        self._saved_lost_progress = 0
        self.previous_full_screen = np.zeros((3, training_screen_size[1], training_screen_size[0]), dtype=np.uint8)
        self.gear_comparer = GearImageComparer()


    def get_next_step(self):
        images = self.screen_grabber.get_images()
        screenshot_time = time.time()
        current_time_to_travel = self._get_current_time_to_travel(images[0])
        max_speed = self._get_max_speed(images[self.screen_grabber.get_max_speed_image_index()])
        current_speed = self._get_current_speed(images[self.screen_grabber.get_current_speed_image_index()])
        info_title = self._read_from_info_title_region(images[self.screen_grabber.get_info_title_image_index()])
        current_gear = self._read_current_gear(images[self.screen_grabber.get_current_gear_image_index()])
        gps_region = images[self.screen_grabber.get_gps_info_image_index()]
        whole_screen_resized = np.transpose(images[self.screen_grabber.get_whole_screen_resized_image_index()], (2, 0, 1))
        gps_region_resized = np.transpose(self.screen_grabber.resize_gps_region(gps_region), (2, 0, 1))
        penalty_score = 0
        #todo wsme: need to add behaviour for if you want to take ferry, rest, ... best to add in the environment itself NOT HERE
        if info_title == ImageSimilarityMatch.INFO and screenshot_time - self.last_info_detected_time > INFO_DETECTED_TIMEOUT_SECONDS:
            print("is info", info_title)
            penalty_score = self._extract_penalty_score_from_extra_information_from_gps(gps_region)
            self.last_info_detected_time = screenshot_time
        prev_screen = self.previous_full_screen
        self.previous_full_screen = whole_screen_resized
        return current_time_to_travel, max_speed, current_speed, info_title, penalty_score, whole_screen_resized, prev_screen, current_gear, gps_region_resized
    
    def get_resized_screenshot(self):
        return self.screen_grabber.get_images()[4]
        
    def _read_from_info_title_region(self, info_title_image):
        currentInfoTitle = self.image_info_comparer.compare_info_image(info_title_image)
        match currentInfoTitle:
            case ImageSimilarityMatch.FERRY | ImageSimilarityMatch.PARKING_LOT | ImageSimilarityMatch.FUEL_STOP:
                return currentInfoTitle
            case ImageSimilarityMatch.NO_MATCH | ImageSimilarityMatch.INFO:
                return currentInfoTitle
    
    def _read_current_gear(self, current_gear_image):
        return self.gear_comparer.get_current_gear(current_gear_image)

    def _get_current_time_to_travel(self, info_image):
        currentInfoString = pytesseract.image_to_string(image=info_image)
        #sometimes the 5 get's read as an S, no other S should be present -> eazy fix is to replace S with 5
        currentInfoString = currentInfoString.replace("S", "5")
        splitInfo = currentInfoString.split(",")
        if len(splitInfo) > 2:
            timeInfo = splitInfo[2] # rest is information about the time of day and which day
            return self._extract_time_in_min_from_game_time(timeInfo)
        else:
            return None

    def _extract_time_in_min_from_game_time(self, gameTimeString):
        try:
            gameTimeString = gameTimeString.replace("\n", "").replace("\t", "")
            timeInMins = 0
            for chars in gameTimeString.split(" "):
                if chars:
                    if len(chars) > 1 and chars[-1] == "h":
                        timeInMins += int(chars[:-1]) * 60
                    elif len(chars) > 3 and chars[-3:] == "min":
                        timeInMins += int(chars[:-3])
            return timeInMins
        except:
            return None
                

    def _get_max_speed(self, max_speed):
        return self._extract_digits(pytesseract.image_to_string(image=max_speed))

    def _get_current_speed(self, speed_image):
        return self._extract_digits(pytesseract.image_to_string(image=speed_image))
    
    def _extract_digits(self, string):
        num = ""
        for char in string:
            if char.isdigit():
                num += char
        if num != "":
            return int(num)
        else:
            return 0
    
    def _extract_penalty_score_from_extra_information_from_gps(self, image):
        detectedText = pytesseract.image_to_string(image=image)
        match = re.search(r"-€(\d+)", detectedText)
        if match:
            return self._fine_to_penalty_score(match.group(1))
        
        match = re.search(r"damage\s+(\d+)\s*%", detectedText, re.IGNORECASE)
        if match:
            return self._damage_to_penalty_score(match.group(1))
        return 0
    
    def calculate_position_reward_score(self, prev_time_to_travel, current_time_to_travel, current_speed):
        if prev_time_to_travel is None or current_time_to_travel is None:
            return 0
        progress = prev_time_to_travel - current_time_to_travel
        progress_reward = progress * 100
        speed_reward = current_speed / 10
        reward =  progress_reward + speed_reward
        #sometimes wrongfully detected -> if it isn't corrected in the next step -> do punish
        if self._saved_lost_progress > 0:
            if progress + 1 >= self._saved_lost_progress and progress - 1 <= self._saved_lost_progress: #check if is around the same
                #lost progress has been corrected
                self._saved_lost_progress = 0
                return speed_reward
            else:
                #did in fact go the wrong way
                if reward < -100:
                    reward = -100
                print_colored(f"Penalty for going the wrong way: {reward}", TerminalColors.PENALTY)
                self._saved_lost_progress = 0
                return reward
        elif progress < 0:
            #save lost progress, might have gone wrong way. Let's see if it has been corrected in the next step
            self._saved_lost_progress = -progress
            return speed_reward   
        else:
            return reward         
    
    def _fine_to_penalty_score(self, fine):
        #fine's can go as high as €5000
        fine_numb = int(fine)
        if fine_numb <= 0:
            return 0
        else:
            #no finei
            if  fine_numb > 5000:
                fine_numb = 5000
            penalty = int(fine) / 5
            print_colored(f"Penalty from fine: {penalty}", TerminalColors.PENALTY)
            return penalty
    
    def _damage_to_penalty_score(self, damage):
        damage = int(damage)
        if damage <= 0:
            return 0
        else:
            if damage > 100:
                damage = 100
            penalty = int(damage) * 10
            print_colored(f"Penalty from damage: {penalty}", TerminalColors.PENALTY)
            return penalty
    


    def diplay_images_debug(self):
        try:
            # Get the images
            images = self.screen_grabber.get_images()

            # Check if the images array is empty
            if not images or not any(img is not None for img in images):
                print("No images to display.")
                return

            # Define screen constraints
            screen_height = 900  # Maximum screen height
            max_width = 1200     # Maximum screen width

            # Process and scale images
            total_height = 0
            scaled_images = []
            for img in images:
                if img is not None:
                    # Convert grayscale to BGR if necessary
                    if len(img.shape) == 2:  # Grayscale image
                        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

                    # Calculate scaling factor
                    scale = min(screen_height / (len(images) * img.shape[0]), max_width / img.shape[1])
                    new_width = int(img.shape[1] * scale)
                    new_height = int(img.shape[0] * scale)
                    resized_img = cv2.resize(img, (new_width, new_height))

                    # Add padding to match the maximum width
                    padded_img = cv2.copyMakeBorder(
                        resized_img,
                        0, 0, 0, max_width - new_width,
                        borderType=cv2.BORDER_CONSTANT,
                        value=(0, 0, 0)  # Black padding
                    )
                    scaled_images.append(padded_img)
                    total_height += new_height
                else:
                    # Add a blank placeholder for None images
                    blank_height = int(screen_height / len(images))
                    scaled_images.append(np.zeros((blank_height, max_width, 3), dtype=np.uint8))
                    total_height += blank_height

            # Concatenate all images vertically
            combined_image = cv2.vconcat(scaled_images)

            # Display the combined image
            cv2.imshow("All Images Vertically Scaled", combined_image)

            # Wait for a key press and close the window
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        except Exception as e:
            print(f"An error occurred while displaying images: {e}")

    def set_right_left_hand_drive(self):
        left_hand_drive_cursor_image = self.screen_grabber.get_left_hand_drive_region_image()
        right_hand_drive_cursor_image = self.screen_grabber.get_right_hand_drive_region_image()
        left_right_hand_drive_match = self.right_left_hand_comparer.get_left_right_hand_drive_type(left_hand_drive_cursor_image, right_hand_drive_cursor_image)
        if left_right_hand_drive_match == RightLeftHandDriveType.LEFT:
            self.screen_grabber.update_left_right_hand_drive(RightLeftHandDriveType.LEFT)
        elif left_right_hand_drive_match == RightLeftHandDriveType.RIGHT:
            self.screen_grabber.update_left_right_hand_drive(RightLeftHandDriveType.RIGHT)
        else:
            print_colored(f"WARNING: neither left nor right hand drive detected, individual mathes were {left_right_hand_drive_match}", TerminalColors.WARNING)


            

if __name__ == "__main__":
    print("Starting from step_interpreter")
    stepInt = StepInterpreter()

    for i in range(0,100):
        stepInt.set_right_left_hand_drive()
        # stepInt.screen_grabber._left_right_hand_drive_type = RightLeftHandDriveType.LEFT
        # stepInt.diplay_images_debug()
        current_time_to_travel, max_speed, current_speed, info_title, penalty_score, whole_screen_resized, prev_screen, current_gear = stepInt.get_next_step()
        print(current_gear)
        time.sleep(2)