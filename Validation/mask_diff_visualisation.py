import cv2
import numpy as np

from Constants import colors


def visualize(hypothesis_image_path, ground_truth_image_path, original_image_path, output_diff_path,
              output_merged_path):
    orig_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    hyp_mask_img_grayscale = cv2.imread(hypothesis_image_path, cv2.IMREAD_GRAYSCALE)
    gt_mask_img = cv2.imread(ground_truth_image_path, cv2.IMREAD_GRAYSCALE)

    _, groundtruth = cv2.threshold(gt_mask_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, predicted = cv2.threshold(hyp_mask_img_grayscale, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Creating image with highlighted TP,TN,FP,FN bubbles
    # GREEN: TP
    # BLACK: TN
    # RED: FP
    # BLUE: FN

    height, width = groundtruth.shape
    result_image = np.zeros((height, width, 3), np.uint8)

    predicted = predicted / 255  # 8b value to binary value: 0-255 -> 0-1
    groundtruth = groundtruth / 255  # 8b value to binary value: 0-255 -> 0-1

    false_positive = predicted - groundtruth
    false_positive[false_positive < 0] = 0

    true_positive = predicted * groundtruth
    false_negative = groundtruth - predicted

    result_image[false_positive == 1] = colors.diff_red
    result_image[true_positive == 1] = colors.diff_green
    result_image[false_negative == 1] = colors.diff_blue

    cv2.imwrite(output_diff_path, result_image)

    # Merging result image with original image
    merged_img = cv2.addWeighted(result_image, 0.4, orig_img, 0.1, 0)
    cv2.imwrite(output_merged_path, merged_img)
