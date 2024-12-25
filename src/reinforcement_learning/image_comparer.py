import cv2
from skimage.metrics import structural_similarity as compare_ssim
from reinforcement_learning.screen_grabber import ScreenGrabber
import time

class ImageInfoComparer:
    def __init__(self):
        self._ferry_image = cv2.imread("resources/ferryInfoText.png", cv2.IMREAD_GRAYSCALE)
        self._info_image = cv2.imread("resources/infoInfoText.png", cv2.IMREAD_GRAYSCALE) #sometimes the title just says info, e.g. with fine information
        self._parking_lot_image = cv2.imread("resources/parkingLotInfoText.png", cv2.IMREAD_GRAYSCALE)
        self._fuel_stop = cv2.imread("resources/fuelStopText.png", cv2.IMREAD_GRAYSCALE)

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

    
class ImageSimilarityMatch:
    NO_MATCH = 0,
    FERRY = 1,
    INFO = 2,
    PARKING_LOT = 3,
    FUEL_STOP = 4

class CursorOnDriveComparer:
    def __init__(self):
        self._cursor_on_drive_image = cv2.imread("resources/cursorOnDrive.png", cv2.IMREAD_GRAYSCALE)
    
    def compare_cursor_on_drive(self, image_to_compare):
        image_to_compare = convert_to_grayscale_if_needed(image_to_compare)
        simmilarity, _ = compare_ssim(image_to_compare, self._cursor_on_drive_image, full=True)
        if simmilarity > 0.8:
            return True
        return False

def convert_to_grayscale_if_needed(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

if "__main__" == __name__:

    def test_cursor_on_drive_comparer():
        comparer = CursorOnDriveComparer()
        screen_grabber = ScreenGrabber()
        similarity_score = comparer.compare_cursor_on_drive(screen_grabber.get_cursor_on_drive_region())
        print(f"Similarity score: {similarity_score}")
        if similarity_score > 0.8:
            print("The images are quite similar.")
        else:
            print("The images are not very similar.")
    for i in range(0,20):
        test_cursor_on_drive_comparer()
        time.sleep(2)