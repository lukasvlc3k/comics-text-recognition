import math

import json
import os.path

import editdistance
import re

from Validation.wer import wer


# unified class containing important data for bubble OCR validation
class OCRData:
    def __init__(self, x, y, w, h, text, confidence):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.confidence = confidence


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def compute_text_metrics(path_ground_truth, path_hypothesis):
    return compute_text_metrics_full(path_ground_truth, path_hypothesis)


def compute_text_metrics_full(path_ground_truth, path_hypothesis):
    gt_texts = []
    hypothesis_texts = []

    if not os.path.isfile(path_hypothesis) or not os.path.isfile(path_ground_truth):
        return -1, -1, -1, -1, -1, -1

    with open(path_ground_truth, "r") as f_gt:
        with open(path_hypothesis, "r") as f_hyp:
            gt_content = f_gt.read()
            hyp_content = f_hyp.read()

            gt_json = json.loads(gt_content)
            hyp_json = json.loads(hyp_content)

            for entry in gt_json:
                gt_texts.append(
                    OCRData(entry["coordX"], entry["coordY"], entry["pixelWidth"], entry["pixelHeight"], entry["text"],
                            1.0))

            for entry in hyp_json:
                hypothesis_texts.append(
                    OCRData(entry["bubbleInfo"]["boundingBox"]["x"], entry["bubbleInfo"]["boundingBox"]["y"],
                            entry["bubbleInfo"]["boundingBox"]["width"], entry["bubbleInfo"]["boundingBox"]["height"],
                            entry["ocr"]["text"], float(entry["ocr"]["avgConfidence"])))

    gt_sorted = sorted(gt_texts, key=lambda data: (data.y, data.x))
    hyp_sorted = sorted(hypothesis_texts, key=lambda data: (data.y, data.x))

    gt_full = ""
    hyp_full = ""

    for gt in gt_sorted:
        gt_full += " " + sanitize(gt.text)
    for hyp in hyp_sorted:
        hyp_full += " " + sanitize(hyp.text)

    gt_full = re.sub('\\s+', ' ', gt_full)
    hyp_full = re.sub('\\s+', ' ', hyp_full)

    print(gt_full)
    print(hyp_full)

    avg_wer = wer(gt_full.split(), hyp_full.split())
    avg_cer = wer(list(gt_full), list(hyp_full))
    avg_ed = editdistance.eval(hyp_full, gt_full)
    return avg_wer, avg_cer, avg_ed, avg_wer, avg_cer, avg_ed


def compute_text_metrics_by_bubbles(path_ground_truth, path_hypothesis):
    gt_texts = []
    hypothesis_texts = []

    if not os.path.isfile(path_hypothesis) or not os.path.isfile(path_ground_truth):
        return -1, -1, -1, -1, -1, -1

    with open(path_ground_truth, "r") as f_gt:
        with open(path_hypothesis, "r") as f_hyp:
            gt_content = f_gt.read()
            hyp_content = f_hyp.read()

            gt_json = json.loads(gt_content)
            hyp_json = json.loads(hyp_content)

            for entry in gt_json:
                gt_texts.append(
                    OCRData(entry["coordX"], entry["coordY"], entry["pixelWidth"], entry["pixelHeight"], entry["text"],
                            1.0))

            for entry in hyp_json:
                hypothesis_texts.append(
                    OCRData(entry["bubbleInfo"]["boundingBox"]["x"], entry["bubbleInfo"]["boundingBox"]["y"],
                            entry["bubbleInfo"]["boundingBox"]["width"], entry["bubbleInfo"]["boundingBox"]["height"],
                            entry["ocr"]["text"], float(entry["ocr"]["avgConfidence"])))

    sum_wer = 0
    count_wer = 0
    sum_cer = 0
    count_cer = 0
    sum_ed = 0
    count_ed = 0

    sum_wer_w = 0
    count_wer_w = 0
    sum_cer_w = 0
    count_cer_w = 0
    sum_ed_w = 0
    count_ed_w = 0

    list_hypothesis = []
    list_gt = []

    for hypothesis in hypothesis_texts:
        gt = find_nearest_gt(hypothesis, gt_texts)
        if gt is None:
            gt_text = ""
        else:
            gt_text = sanitize(gt.text)

        hypothesis_text = sanitize(hypothesis.text)

        list_gt.append(gt_text)
        list_hypothesis.append(hypothesis_text)

        if gt_text == "":
            current_ed = 0
            current_wer = 1
            current_cer = 1
        else:
            current_ed = editdistance.eval(hypothesis_text, gt_text)
            current_wer = wer(gt_text.split(" "), hypothesis_text.split(" "))
            current_cer = wer(list(gt_text), list(hypothesis_text))

        sum_wer += current_wer
        sum_cer += current_cer
        sum_ed += current_ed
        count_wer += 1
        count_cer += 1
        count_ed += 1

        w = max(len(gt_text), len(hypothesis_text))
        sum_wer_w += current_wer * w
        sum_cer_w += current_cer * w
        sum_ed_w += current_ed * w
        count_wer_w += w
        count_cer_w += w
        count_ed_w += w

    avg_wer = sum_wer / count_wer if count_wer > 0 else 0
    avg_cer = sum_cer / count_cer if count_cer > 0 else 0
    avg_ed = sum_ed / count_ed if count_ed > 0 else 0

    avg_wer_conf = sum_wer_w / count_wer_w if count_wer_w > 0 else 0
    avg_cer_conf = sum_cer_w / count_cer_w if count_cer_w > 0 else 0
    avg_ed_conf = sum_ed_w / count_ed_w if count_ed_w > 0 else 0

    return avg_wer, avg_cer, avg_ed, avg_wer_conf, avg_cer_conf, avg_ed_conf


# function computes whether two rectangles overlap
def do_overlap(l1, r1, l2, r2):
    return (l1.x < r2.x and r1.x > l2.x and
            l1.y < r2.y and r1.y > l2.y)


# function that finds the nearest gt for bubble
def find_nearest_gt(hypothesis: OCRData, gt_texts: []):
    best_distance = float('inf')
    best_gt = None
    hypothesis_center = (hypothesis.x + hypothesis.w / 2, hypothesis.y + hypothesis.h / 2)

    overlaping = []

    for gt in gt_texts:

        l1 = Point(hypothesis.x, hypothesis.y)
        r1 = Point(hypothesis.x + hypothesis.w, hypothesis.y + hypothesis.h)
        l2 = Point(gt.x, gt.y)
        r2 = Point(gt.x + gt.w, gt.y + gt.h)
        overlap = do_overlap(l1, r1, l2, r2)

        if overlap:
            overlaping.append(gt)

    for gt in overlaping:
        gt_center = (gt.x + gt.w / 2, gt.y + gt.h / 2)
        distance = math.sqrt((gt_center[0] - hypothesis_center[0]) ** 2 + (gt_center[1] - hypothesis_center[1]) ** 2)
        if distance < best_distance:
            best_distance = distance
            best_gt = gt

    return best_gt


# function removing all non-alphanumeric characters from string
def sanitize(text):
    text = re.sub(r"\n", " ", text)
    return re.sub('[^0-9a-zA-Z ]+', '', text)
