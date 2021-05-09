import cv2
import os.path

from Exceptions import FileReadException


def load_image(path):
    if not os.path.isfile(path):
        raise FileNotFoundError

    img = cv2.imread(path)
    if img is None:
        raise FileReadException

    return img


def add_candidate_to_final_mask(final_bubble_mask, bubble_candidate):
    cv2.drawContours(final_bubble_mask, [bubble_candidate.get_contour()], 0, (255, 255, 255), cv2.FILLED)


def save_image(path, image):
    cv2.imwrite(path, image)


def canny_edge(img, g_min, g_max):
    return cv2.Canny(img, g_min, g_max)


def dilate(img, shape, size):
    kernel = cv2.getStructuringElement(shape, (size, size))
    return cv2.dilate(img, kernel)


def inverse_single_channel(source_image):
    return 255 - source_image


def mask_image(original_image, value_filter):
    return cv2.inRange(original_image, value_filter, value_filter)


def find_top_contour(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours[0]


def fill_contour(img, contour):
    cv2.drawContours(img, [contour], 0, (255, 255, 255), cv2.FILLED)


def get_contour_area(contour):
    return cv2.contourArea(contour)


def get_perimeter(contour):
    return cv2.arcLength(contour, True)


def get_bounding_box(contour):
    return cv2.boundingRect(contour)


def apply_mask(img, mask):
    return cv2.bitwise_and(img, img, mask=mask)


def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def get_width_height(image):
    return image.shape[1], image.shape[0]
