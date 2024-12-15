from reinforcement_learning.screen_grabber import ScreenGrabber
import pytesseract
import time

class StepInterpreter:
    def __init__(self):
        self.screen_grabber = ScreenGrabber()
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

    def calculate_values(self):
        images = self.screen_grabber.get_regions()
        return self._get_current_time_to_travel(images[0]), self._get_max_speed(images[1]), self._get_current_speed(images[2])

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

if __name__ == "__main__":
    print("Starting from step_interpreter")
    stepInt = StepInterpreter()
    for i in range(0,100):
        stepInt.calculate_values()
        time.sleep(2)