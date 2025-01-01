from reinforcment_learning.screen_grabber import ScreenGrabber
import cv2
import pickle
from reinforcment_learning.image_comparer import convert_to_grayscale_if_needed

def store_current_gear_image():
    print("Starting image collector")
    screen_grabber = ScreenGrabber()
    images = screen_grabber.get_images()
    current_gear_image = images[screen_grabber.get_current_gear_image_index()]
    current_gear_image = convert_to_grayscale_if_needed(current_gear_image)
    pickle.dump(current_gear_image, open("current_gear_image.p", "wb"))
    

if __name__ == "__main__":
    store_current_gear_image()