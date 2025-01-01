import cv2
import numpy as np

def highlight_differences(image1, image2, output_filename="differences.png"):
    """
    Overlays two images and highlights their differences, displaying all images vertically stacked.

    Args:
        image1 (numpy.ndarray): The first image.
        image2 (numpy.ndarray): The second image (same size as the first).
        output_filename (str): Filename for saving the result image.

    Returns:
        numpy.ndarray: The resulting image with differences highlighted.
    """
    # Ensure both images are the same size
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions")

    # Calculate the absolute difference between the two images
    diff_gray = cv2.absdiff(image1, image2)

    # Stack images vertically
    stacked_images = np.vstack((image1, image2, diff_gray))

    # Display the images in a single window
    cv2.imshow("Image Comparison", stacked_images)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save the stacked image
    cv2.imwrite(output_filename, stacked_images)
    print(f"All images displayed and saved as {output_filename}")

    return stacked_images
