from reinforcement_learning.screen_grabber import ScreenGrabber
import pytesseract
import time

class StepInterpreter:
    def __init__(self):
        self.screen_grabber = ScreenGrabber()
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

    def calculate_values(self):
        images = self.screen_grabber.get_regions()
        self._get_current_info(images[0])
        # self._get_max_speed(images[1])
        # self._get_current_speed(images[2])

    def _get_current_info(self, info_image):
        print(pytesseract.image_to_string(image=info_image))

    def _get_max_speed(self, max_speed):
        print(pytesseract.image_to_string(image=max_speed))

    def _get_current_speed(self, speed_image):
        print(pytesseract.image_to_string(image=speed_image))


if __name__ == "__main__":
    print("Starting from step_interpreter")
    stepInt = StepInterpreter()
    for i in range(0,100):
        stepInt.calculate_values()
        time.sleep(2)