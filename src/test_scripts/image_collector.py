from reinforcment_learning.screen_grabber import ScreenGrabber
import cv2

def store_current_gear_image():
    print("Starting image collector")
    screen_grabber = ScreenGrabber()
    images = screen_grabber.get_images()
    current_gear_image = images[screen_grabber.get_current_gear_image_index()]
    cv2.imwrite("current_gear_image.png", cv2.cvtColor(current_gear_image, cv2.COLOR_RGB2BGR))
    

if __name__ == "__main__":
    store_current_gear_image()