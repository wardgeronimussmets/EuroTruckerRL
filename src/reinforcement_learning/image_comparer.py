import cv2
from skimage.metrics import structural_similarity as compare_ssim
from reinforcement_learning.screen_grabber import ScreenGrabber
from reinforcement_learning.types import RightLeftHandDriveType, ImageSimilarityMatch
import time

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

    for i in range(0,20):
        test_info_comparer()
        time.sleep(2)