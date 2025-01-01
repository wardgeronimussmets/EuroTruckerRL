import cv2
from skimage.metrics import structural_similarity as compare_ssim
from reinforcment_learning.screen_grabber import ScreenGrabber
from reinforcment_learning.types import RightLeftHandDriveType, ImageSimilarityMatch
import time
from PIL import Image, ImageOps
import numpy as np
from reinforcment_learning.terminal import print_colored, TerminalColors
from test_scripts.image_visualiser import highlight_differences
import pickle

class ImageInfoComparer:
    def __init__(self):
        self._ferry_image = cv2.imread("resources/ferryInfoText.png", cv2.IMREAD_GRAYSCALE)
        self._info_image = cv2.imread("resources/infoInfoText.png", cv2.IMREAD_GRAYSCALE) #sometimes the title just says info, e.g. with fine information
        self._parking_lot_image = cv2.imread("resources/parkingLotInfoText.png", cv2.IMREAD_GRAYSCALE)
        self._fuel_stop = cv2.imread("resources/fuelStopText.png", cv2.IMREAD_GRAYSCALE)
        self.fit_images_to_correct_size()
        
    def fit_images_to_correct_size(self):
        screen_grabber = ScreenGrabber()
        test_image = screen_grabber.get_images()[screen_grabber.get_info_title_image_index()]
        test_image = convert_to_grayscale_if_needed(test_image)
        if test_image.shape != self._ferry_image.shape:
            print("Resizing info detection images to correct size")
            self._ferry_image = resize_image(self._ferry_image, test_image.shape)
            self._info_image = resize_image(self._info_image, test_image.shape)
            self._parking_lot_image = resize_image(self._parking_lot_image, test_image.shape)
            self._fuel_stop = resize_image(self._fuel_stop, test_image.shape)

    def compare_info_image(self, image_to_compare):
        """
        Compares the given image with the ferry, info, and parking lot images.
        Args:
        - image_to_compare (numpy.ndarray): The image to compare, in color format.
        Returns:
        - similarity (ImageSimilarityMatch): If the image is similar enough for a match: true or false.
        """
        image_to_compare = convert_to_grayscale_if_needed(image_to_compare)
        images = [self._ferry_image, self._info_image, self._parking_lot_image, self._fuel_stop]
        image_matches = [ImageSimilarityMatch.FERRY, ImageSimilarityMatch.INFO, ImageSimilarityMatch.PARKING_LOT, ImageSimilarityMatch.FUEL_STOP]
        for i in range(len(images)):
            similarity, _ = compare_ssim(image_to_compare, images[i], full=True)
            if similarity > 0.8:
                return image_matches[i]
        return ImageSimilarityMatch.NO_MATCH



class CursorOnDriveComparer:
    def __init__(self):
        self._cursor_on_drive_image = cv2.imread("resources/cursorOnDrive.png", cv2.IMREAD_GRAYSCALE)
        self.fit_images_to_correct_size()
        
    def fit_images_to_correct_size(self):
        screen_grabber = ScreenGrabber()
        test_image = screen_grabber.get_cursor_on_drive_image()
        test_image = convert_to_grayscale_if_needed(test_image)
        if test_image.shape != self._cursor_on_drive_image.shape:
            print("Resizing cursor on drive image to correct size")
            self._cursor_on_drive_image = resize_image(self._cursor_on_drive_image, test_image.shape)
    
    def compare_cursor_on_drive(self, image_to_compare):
        image_to_compare = convert_to_grayscale_if_needed(image_to_compare)
        simmilarity, _ = compare_ssim(image_to_compare, self._cursor_on_drive_image, full=True)
        if simmilarity > 0.8:
            return True
        return False
    
class RightLeftHandDriveComparer:
    def __init__(self):
        self.left_hand_drive_image = cv2.imread("resources/leftHandDriveDetector.png", cv2.IMREAD_GRAYSCALE)
        self.right_hand_drive_image = cv2.imread("resources/rightHandDriveDetector.png", cv2.IMREAD_GRAYSCALE)
        self.fit_images_to_correct_size()
        
    def fit_images_to_correct_size(self):
        screen_grabber = ScreenGrabber()
        test_image = screen_grabber.get_left_hand_drive_region_image()
        test_image = convert_to_grayscale_if_needed(test_image)        
        if test_image.shape != self.left_hand_drive_image.shape:
            print("Resizing left hand drive image to correct size")
            self.left_hand_drive_image = resize_image(self.left_hand_drive_image, test_image.shape)
        if test_image.shape != self.right_hand_drive_image.shape:
            print("Resizing right hand drive image to correct size")
            self.right_hand_drive_image = resize_image(self.right_hand_drive_image, test_image.shape)

    def get_left_right_hand_drive_type(self, left_hand_drive_image, right_hand_drive_image):
        left_hand_drive_image_to_compare = convert_to_grayscale_if_needed(left_hand_drive_image)
        right_hand_drive_image_to_compare = convert_to_grayscale_if_needed(right_hand_drive_image)
        left_similarity, _ = compare_ssim(left_hand_drive_image_to_compare, self.left_hand_drive_image, full=True)
        right_similarity, _ = compare_ssim(right_hand_drive_image_to_compare, self.right_hand_drive_image, full=True)
        if left_similarity > right_similarity and left_similarity > 0.8:
            return RightLeftHandDriveType.LEFT
        elif right_similarity > left_similarity and right_similarity > 0.8:
            return RightLeftHandDriveType.RIGHT
        else:
            return RightLeftHandDriveType.NONE
        
class GearImageComparer:
    #assuming 12 forward + 4 reverse is maximum with 4 is neutral
    TOTAL_AMOUNT_OF_GEARS = 17
    def __init__(self):
        #using pickle instead of images because changes occur between saving and loading an image
        self.gear_n_image = cv2.imread("resources/gear_N.png", cv2.IMREAD_COLOR)
        self.gear_n_image = cv2.cvtColor(self.gear_n_image, cv2.COLOR_BGR2GRAY)
        self.gear_1_image = cv2.imread("resources/gear_1.png", cv2.IMREAD_GRAYSCALE)
        self.gear_2_image = cv2.imread("resources/gear_2.png", cv2.IMREAD_GRAYSCALE)
        self.gear_3_image = cv2.imread("resources/gear_3.png", cv2.IMREAD_GRAYSCALE)
        self.gear_4_image = cv2.imread("resources/gear_4.png", cv2.IMREAD_GRAYSCALE)
        self.gear_5_image = cv2.imread("resources/gear_5.png", cv2.IMREAD_GRAYSCALE)
        self.gear_6_image = cv2.imread("resources/gear_6.png", cv2.IMREAD_GRAYSCALE)
        self.gear_7_image = cv2.imread("resources/gear_7.png", cv2.IMREAD_GRAYSCALE)
        self.gear_8_image = cv2.imread("resources/gear_8.png", cv2.IMREAD_GRAYSCALE)
        self.gear_9_image = cv2.imread("resources/gear_9.png", cv2.IMREAD_GRAYSCALE)
        self.gear_10_image = cv2.imread("resources/gear_10.png", cv2.IMREAD_GRAYSCALE)
        self.gear_11_image = cv2.imread("resources/gear_11.png", cv2.IMREAD_GRAYSCALE)
        self.gear_12_image = cv2.imread("resources/gear_12.png", cv2.IMREAD_GRAYSCALE)
        self.gear_r1_image = cv2.imread("resources/gear_r1.png", cv2.IMREAD_GRAYSCALE)
        self.gear_r2_image = cv2.imread("resources/gear_r2.png", cv2.IMREAD_GRAYSCALE)
        self.gear_r3_image = cv2.imread("resources/gear_r3.png", cv2.IMREAD_GRAYSCALE)
        self.gear_r4_image = cv2.imread("resources/gear_r4.png", cv2.IMREAD_GRAYSCALE)
        self._fit_images_to_correct_size()
        self.previous_gear = 4
    
    def _fit_images_to_correct_size(self):
        screen_grabber = ScreenGrabber()
        test_image = screen_grabber.get_images()[screen_grabber.get_current_gear_image_index()]
        test_image = convert_to_grayscale_if_needed(test_image)        
        if test_image.shape != self.gear_n_image.shape:
            print("Resizing gear detection images to correct size")
            self.gear_n_image = resize_image(self.gear_n_image, test_image.shape)
            self.gear_1_image = resize_image(self.gear_1_image, test_image.shape)
            self.gear_2_image = resize_image(self.gear_2_image, test_image.shape)
            self.gear_3_image = resize_image(self.gear_3_image, test_image.shape)
            self.gear_4_image = resize_image(self.gear_4_image, test_image.shape)
            self.gear_5_image = resize_image(self.gear_5_image, test_image.shape)
            self.gear_6_image = resize_image(self.gear_6_image, test_image.shape)
            self.gear_7_image = resize_image(self.gear_7_image, test_image.shape)            
            self.gear_8_image = resize_image(self.gear_8_image, test_image.shape)
            self.gear_9_image = resize_image(self.gear_9_image, test_image.shape)
            self.gear_10_image = resize_image(self.gear_10_image, test_image.shape)
            self.gear_11_image = resize_image(self.gear_11_image, test_image.shape)
            self.gear_12_image = resize_image(self.gear_12_image, test_image.shape)
            self.gear_r1_image = resize_image(self.gear_r1_image, test_image.shape)
            self.gear_r2_image = resize_image(self.gear_r2_image, test_image.shape)
            self.gear_r3_image = resize_image(self.gear_r3_image, test_image.shape)
            self.gear_r4_image = resize_image(self.gear_r4_image, test_image.shape)
            
    def _gear_numb_to_image(self, gear_number):
        match gear_number:
            case 0:
                return self.gear_r4_image
            case 1:
                return self.gear_r3_image
            case 2:
                return self.gear_r2_image
            case 3:
                return self.gear_r1_image
            case 4:
                return self.gear_n_image
            case 5:
                return self.gear_1_image
            case 6:
                return self.gear_2_image
            case 7:
                return self.gear_3_image
            case 8:
                return self.gear_4_image
            case 9:
                return self.gear_5_image
            case 10:
                return self.gear_6_image
            case 11:            
                return self.gear_7_image
            case 12:
                return self.gear_8_image
            case 13:
                return self.gear_9_image
            case 14:
                return self.gear_10_image
            case 15:
                return self.gear_11_image
            case 16:
                return self.gear_12_image
        return self.gear_n_image
    
    def get_current_gear(self, image_to_compare):
        image_to_compare = convert_to_grayscale_if_needed(image_to_compare)   
        
        highlight_differences(image_to_compare, self._gear_numb_to_image(4), "current_gear.png")     
        
        own_gear = self._gear_numb_to_image(self.previous_gear)
        if self._check_if_correct_gear(image_to_compare, own_gear):
            return self.previous_gear
        else:
            lower_gear = self.previous_gear
            higher_gear = self.previous_gear
            
            while lower_gear >= 0 or higher_gear < GearImageComparer.TOTAL_AMOUNT_OF_GEARS:
                lower_gear -= 1
                higher_gear += 1
                if lower_gear >= 0:
                    if self._check_if_correct_gear(image_to_compare, self._gear_numb_to_image(lower_gear)):
                        self.previous_gear = lower_gear
                        return lower_gear
                if higher_gear < GearImageComparer.TOTAL_AMOUNT_OF_GEARS:
                    if self._check_if_correct_gear(image_to_compare, self._gear_numb_to_image(higher_gear)):
                        self.previous_gear = higher_gear
                        return higher_gear
        print_colored("Could not find current gear, defaulting to previous gear", TerminalColors.WARNING)
        return self.previous_gear
    
    def _check_if_correct_gear(self, im1, im2):
        similarity, _ = compare_ssim(im1, im2, full=True)
        if similarity > 0.92:
            print("similarity", similarity)
            return True
        return False


def convert_to_grayscale_if_needed(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def resize_image(image_to_resize, target_shape):
    # Read the image
    if image_to_resize is None:
        raise ValueError("Image not found or unable to read")
    return cv2.resize(image_to_resize, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_LINEAR)


if "__main__" == __name__:
    def test_cursor_on_drive_comparer():
        comparer = CursorOnDriveComparer()
        screen_grabber = ScreenGrabber()
        similarity_score = comparer.compare_cursor_on_drive(screen_grabber.get_cursor_on_drive_image())
        print(f"Similarity score: {similarity_score}")
        if similarity_score > 0.8:
            print("The images are quite similar.")
        else:
            print("The images are not very similar.")

    def test_info_comparer():
        comparer = ImageInfoComparer()
        screen_grabber = ScreenGrabber(left_right_hand_drive_type=RightLeftHandDriveType.RIGHT)
        similarity_score = comparer.compare_info_image(screen_grabber.get_images()[screen_grabber.get_info_title_image_index()])
        print(f"Similarity score: {similarity_score}")
        
    def test_gear_comparer():
        comparer = GearImageComparer()
        screen_grabber = ScreenGrabber(left_right_hand_drive_type=RightLeftHandDriveType.RIGHT)
        for i in range(0,50):
            run_test_comparer(comparer, screen_grabber)
            time.sleep(1)
            print("                                ")
    
    def run_test_comparer(comparer:GearImageComparer, screen_grabber:ScreenGrabber):
        gear = comparer.get_current_gear(screen_grabber.get_images()[screen_grabber.get_current_gear_image_index()])
        print(f"Gear: {gear}")


    test_gear_comparer()
