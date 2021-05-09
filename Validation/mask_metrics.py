import numpy as np


def compute_metrics(predicted, groundtruth):
    predicted = predicted / 255
    groundtruth = groundtruth / 255

    # inverted ground truth
    # all numbers incremented (0 --> 1, 1 --> 2) and then 2 --> 0
    groundtruth_inverse = groundtruth + 1
    groundtruth_inverse[groundtruth_inverse > 1] = 0

    # inverted prediction
    # all numbers incremented (0 --> 1, 1 --> 2) and then 2 --> 0
    predicted_inverse = predicted + 1
    predicted_inverse[predicted_inverse > 1] = 0

    # Foreground - true positive
    tp_foreground = np.sum(groundtruth * predicted)

    # Foreground - false positive
    fp_foreground = np.sum(groundtruth_inverse * predicted)

    # false negative
    falsenegative_foreground = np.sum(groundtruth * predicted_inverse)  # zeros in pred and ones in gt

    f1_foreground = 2 * tp_foreground / (
            2 * tp_foreground + fp_foreground + falsenegative_foreground)
    # print("F1 - foreground: ", f1_foreground)

    # Background - true positive
    tp_background = np.sum(groundtruth_inverse * predicted_inverse)

    # Background - false positive
    fp_background = np.sum(groundtruth * predicted_inverse)  # ones in predInv, zeros in gtInv = ones in gt

    # Background - false positive
    fn_background = np.sum(predicted * groundtruth_inverse)  # zeros in predInv = ones in pred, ones in gtInv =

    f1_background = 2 * tp_background / (2 * tp_background + fp_background + fn_background)

    # print("F1 - background: ", f1_background)

    # IMAGES without foreground
    if f1_foreground == 0 and np.max(groundtruth) == 0:
        f1 = f1_background
    else:
        f1 = (f1_foreground + f1_background) / 2

    # Intersection over Union -- Jaccard index
    iou_foreground = tp_foreground / (
            tp_foreground + fp_foreground + falsenegative_foreground)
    iou_background = tp_background / (tp_background + fp_background + fn_background)

    # IMAGES without foreground
    if iou_foreground == 0 and np.max(groundtruth) == 0:
        iou_foreground = 1

    iou = (iou_foreground + iou_background) / 2

    return f1, iou
