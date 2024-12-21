from reinforcement_learning.screen_grabber import ScreenGrabber
from reinforcement_learning.image_comparer import ImageInfoComparer, ImageSimilarityMatch
import pytesseract
import time
import re

INFO_DETECTED_TIMEOUT_SECONDS = 2.5 #Don't detect fines multiple times

class StepInterpreter:
    def __init__(self):
        self.screen_grabber = ScreenGrabber()
        self.image_info_comparer = ImageInfoComparer()
        self.last_info_detected_time = 0 #info detection should be time as to not detect it multiple times
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

    def calculate_values(self):
        images = self.screen_grabber.get_regions()
        screenshotTime = time.time()
        current_time_to_travel = self._get_current_time_to_travel(images[0])
        max_speed = self._get_max_speed(images[1])
        current_speed = self._get_current_speed(images[2])
        info_title = self._read_from_info_title_region(images[3])
        #todo wsme: need to add behaviour for if you want to take ferry, rest, ... best to add in the environment itself NOT HERE
        if info_title == ImageSimilarityMatch.INFO and screenshotTime - self.last_info_detected_time > INFO_DETECTED_TIMEOUT_SECONDS:
            penalty_score = self._extract_penalty_score_from_extra_information_from_gps(images[4])
            self.last_info_detected_time = screenshotTime
        return current_time_to_travel, max_speed, current_speed, info_title ,penalty_score
        
    def _read_from_info_title_region(self, info_title_image):
        currentInfoTitle = self.image_info_comparer.compare_info_image(info_title_image)
        match currentInfoTitle:
            case ImageSimilarityMatch.FERRY, ImageSimilarityMatch.PARKING_LOT:
                print(currentInfoTitle)
                return currentInfoTitle
            case ImageSimilarityMatch.NO_MATCH:
                return currentInfoTitle
            case ImageSimilarityMatch.INFO:
                print("info")
                

    def _get_current_time_to_travel(self, info_image):
        currentInfoString = pytesseract.image_to_string(image=info_image)
        splitInfo = currentInfoString.split(",")
        if len(splitInfo) > 2:
            timeInfo = splitInfo[2]
            return self._extract_time_in_min_from_game_time(timeInfo)

    def _extract_time_in_min_from_game_time(self, gameTimeString):
        currentNum = 0
        timeInMins = 0
        for chars in gameTimeString.split(" "):
            if chars.isdigit():
                currentNum += int(chars)
            elif chars == "h":
                timeInMins += currentNum * 60
                currentNum = 0
            elif chars == "min":
                timeInMins += currentNum
                currentNum = 0
                

    def _get_max_speed(self, max_speed):
        return self._extract_digits(pytesseract.image_to_string(image=max_speed))

    def _get_current_speed(self, speed_image):
        return self._extract_digits(pytesseract.image_to_string(image=speed_image))
    
    def _extract_digits(self, string):
        num = ""
        for char in string:
            if char.isdigit():
                num += char
        return int(num)
    
    def _extract_penalty_score_from_extra_information_from_gps(self, image):
        detectedText = pytesseract.image_to_string(image=image)
        match = re.search(r"-€(\d+)", detectedText)
        if match:
            return self._fine_to_penalty_score(match.group(1))
        
        match = re.search(r"damage\s+(\d+)\s*%", detectedText, re.IGNORECASE)
        if match:
            return self._damage_to_penalty_score(match.group(1))
        return 0
    
    def _fine_to_penalty_score(self, fine):
        #fine's can go as high as €5000
        fine_numb = int(fine)
        if fine_numb < 0:
            return 0
        elif fine_numb > 5000:
            fine_numb = 5000
        return int(fine) / 500
    
    def _damage_to_penalty_score(self, damage):
        damage = int(damage)
        if damage < 0:
            return 0
        if damage > 100:
            damage = 100
        return damage / 10


if __name__ == "__main__":
    print("Starting from step_interpreter")
    stepInt = StepInterpreter()
    for i in range(0,100):
        stepInt.calculate_values()
        time.sleep(2)