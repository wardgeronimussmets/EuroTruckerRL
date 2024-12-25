import cv2
from skimage.metrics import structural_similarity as compare_ssim
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
        image_to_compare = self.convert_to_grayscale_if_needed(image_to_compare)
        images = [self._ferry_image, self._info_image, self._parking_lot_image, self._fuel_stop]
        image_matches = [ImageSimilarityMatch.FERRY, ImageSimilarityMatch.INFO, ImageSimilarityMatch.PARKING_LOT, ImageSimilarityMatch.FUEL_STOP]
        for i in range(len(images)):
            similarity, _ = compare_ssim(image_to_compare, images[i], full=True)
            if similarity > 0.8:
                return image_matches[i]
        return ImageSimilarityMatch.NO_MATCH
    
    def convert_to_grayscale_if_needed(self, image):
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
class ImageSimilarityMatch:
    NO_MATCH = 0,
    FERRY = 1,
    INFO = 2,
    PARKING_LOT = 3,
    FUEL_STOP = 4

def compare_images(image_path1, image_path2, resize_dim=(300, 300)):
    """
    Compares two images for likeness using SSIM (Structural Similarity Index).
    Optimized for performance by resizing images before comparison.

    Args:
    - image_path1 (str): Path to the first image.
    - image_path2 (str): Path to the second image.
    - resize_dim (tuple): Dimensions to resize the images for comparison. Defaults to (300, 300).

    Returns:
    - similarity (float): A value between -1 and 1 indicating the structural similarity. Closer to 1 means more similar.
    """
    # Load the images in grayscale for faster processing
    image1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    if image1 is None or image2 is None:
        raise ValueError("One or both image paths are invalid or the images could not be loaded.")

    # Resize the images to the same dimensions for comparison
    image1_resized = cv2.resize(image1, resize_dim, interpolation=cv2.INTER_LINEAR)
    image2_resized = cv2.resize(image2, resize_dim, interpolation=cv2.INTER_LINEAR)

    # Compute SSIM between the resized images
    similarity, _ = compare_ssim(image1_resized, image2_resized, full=True)

    return similarity

if "__main__" == __name__:
    # Example usage
    image1_path = "resources/ferryInfoText.png"
    image2_path = "resources/infoInfoText.png"

    start_time = time.time()
    similarity_score = compare_images(image1_path, image1_path)
    print("Time elapsed:", time.time() - start_time, "s")


    print(f"Similarity score: {similarity_score}")
    if similarity_score > 0.8:
        print("The images are quite similar.")
    else:
        print("The images are not very similar.")
