import cv2
import numpy as np

from Constants import colors
from Utils.image_utils import get_width_height, mask_image
from Utils.component_detection import get_components


def is_green_nearby(image, x, y) -> bool:
    w, h = get_width_height(image)

    tolerance_pixels = 3
    for ix in range(2 * tolerance_pixels + 1):
        for iy in range(2 * tolerance_pixels + 1):
            x_new = min(max(x + (ix - tolerance_pixels), 0), w - 1)
            y_new = min(max(y + (iy - tolerance_pixels), 0), h - 1)

            if np.all(image[y_new, x_new] == colors.diff_green):
                return True

    return False


def count_components(masked):
    num_labels, labels, stats, centroids = get_components(masked)

    count = 0
    for lbl in range(1, num_labels):
        area = stats[lbl, cv2.CC_STAT_AREA]
        if area < 25:
            continue
        count += 1
    return count


def count_diffs(diff_image_path, updated_diff_path=None):  # tp, fp, fn
    diff_img = cv2.imread(diff_image_path)

    w, h = get_width_height(diff_img)
    mask = np.zeros((h + 2, w + 2), np.uint8)

    false_negative = mask_image(diff_img, colors.diff_blue)
    for y in range(diff_img.shape[0]):
        for x in range(diff_img.shape[1]):
            if np.all(diff_img[y, x] == colors.diff_blue) or np.all(diff_img[y, x] == colors.diff_red):
                if is_green_nearby(diff_img, x, y):
                    cv2.floodFill(diff_img, None, (x, y), (0, 0, 0,))

    false_negative = mask_image(diff_img, colors.diff_blue)
    false_positive = mask_image(diff_img, colors.diff_red)
    true_positive = mask_image(diff_img, colors.diff_green)

    count_fp = count_components(false_positive)
    count_fn = count_components(false_negative)
    count_tp = count_components(true_positive)

    if updated_diff_path is not None:
        cv2.imwrite(updated_diff_path, diff_img)

    return count_tp, count_fp, count_fn
