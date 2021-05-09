import os
import cv2
import comics_processing
import shutil
import os.path
from os import path
import config
import argparse

from Validation import mask_metrics, mask_diff_visualisation
from Validation.text_metrics import compute_text_metrics
from Validation.diff_checker import count_diffs

# validates results according to GT
# test_images_dir: path to directory containing source images (comic pages)
# results_base_dir: path where results will be saved
# masks_base_dir: path to directory containing gt bubble masks, mask file should have the same name as the source image
# ocr_base_dir: path to directory containing gt ocr, excepted ocr gt structure: ocr_base_dir/name/name.json
# instance of ConsoleLogger
from Output.ConsoleLogger import ConsoleLogger, Verbosity


def validate_results(test_images_dir, results_base_dir, masks_base_dir, ocr_base_dir, logger):
    with os.scandir(test_images_dir) as entries:
        for entry in entries:
            file_name = entry.name
            logger.info("Validating " + file_name)

            entry_name, entry_extension = os.path.splitext(entry.name)

            path_original = os.path.join(test_images_dir, file_name)
            path_label = get_label(entry_name, masks_base_dir)
            path_ocr = get_text_gt_path(entry_name, ocr_base_dir)

            if path_label is None:
                logger.warning("\tGT Label not found, skipping")
                continue
            else:
                logger.info("\tGT Label found (" + path_label + ")")

            label_name, label_extension = os.path.splitext(path_label)

            result_dir = os.path.join(results_base_dir, file_name)
            delete_dir_if_exists(result_dir)
            os.mkdir(result_dir)

            path_result_original = os.path.join(result_dir, "original" + entry_extension)
            path_result_label = os.path.join(result_dir, "labels_gt" + label_extension)
            path_result_mask = os.path.join(result_dir, "mask.png")
            path_result_data = os.path.join(result_dir, "data.txt")
            path_result_visualisation = os.path.join(result_dir, "visualisation.png")
            path_result_diff = os.path.join(result_dir, "diff.png")
            path_result_diff_updated = os.path.join(result_dir, "diff_updated.png")
            path_result_info = os.path.join(result_dir, "validation.txt")
            path_result_bubbles = os.path.join(result_dir, "bubbles/")
            path_text_gt = os.path.join(result_dir, "text_gt")

            os.mkdir(path_result_bubbles)

            shutil.copy(path_original, path_result_original)
            shutil.copy(path_label, path_result_label)

            if path_ocr is not None:
                shutil.copy(path_ocr, path_text_gt)

            logger.info("Processing comic page...")
            with open(path_result_data, "w") as f_text:
                comics_processing.process_comic_page(path_result_original, path_result_mask, f_text,
                                                     config, logger, path_result_bubbles)

            img_predicted = cv2.imread(path_result_mask, cv2.IMREAD_GRAYSCALE)
            img_groundtruth = cv2.imread(path_result_label, cv2.IMREAD_GRAYSCALE)
            logger.info("Computing px metrics...")
            f1, iou = mask_metrics.compute_metrics(img_predicted, img_groundtruth)

            logger.info("Computing px visualization...")
            mask_diff_visualisation.visualize(path_result_mask, path_result_label, path_result_original,
                                              path_result_diff,
                                              path_result_visualisation)

            logger.info("Computing TP, FP, FN...")
            true_positives, false_positives, false_negatives = count_diffs(path_result_diff, path_result_diff_updated)

            logger.info("Computing text metrics...")
            wer, cer, ed, wer_w, cer_w, ed_w = compute_text_metrics(path_text_gt, path_result_data)

            logger.info('F1 SCORE = {f1}, Jaccard Index = {jc}'.format(f1=f1, jc=iou))
            logger.info(
                'True positives = {tp}\tFalse positives = {fp}\tFalse negatives = {fn}'.format(tp=true_positives,
                                                                                               fp=false_positives,
                                                                                               fn=false_negatives))
            logger.info('WER = {wer}\nCER = {cer}\nED = {ed}'.format(wer=wer, cer=cer, ed=ed))
            logger.info('WER_w = {wer}\nCER_w = {cer}\nED_w = {ed}'.format(wer=wer_w, cer=cer_w, ed=ed_w))

            # writing results to file
            with open(path_result_info, "w") as f:
                f.write('F1 SCORE = {f1}\nJaccard Index = {jc}\n'.format(f1=f1, jc=iou))
                f.write(
                    'True positives = {tp}\nFalse positives = {fp}\nFalse negatives = {fn}\n'.format(tp=true_positives,
                                                                                                     fp=false_positives,
                                                                                                     fn=false_negatives))
                f.write('WER = {wer}\nCER = {cer}\nED = {ed}\n'.format(wer=wer, cer=cer, ed=ed))
                f.write('WER_w = {wer}\nCER_W = {cer}\nED_w = {ed}'.format(wer=wer_w, cer=cer_w, ed=ed_w))


def delete_dir_if_exists(folder):
    if not os.path.isdir(folder):
        return

    shutil.rmtree(folder)


# find gt bubble mask
def get_label(name, labels_base):
    path_base = os.path.join(labels_base, name)
    if path.exists(path_base + ".png"):
        return path_base + ".png"
    if path.exists(path_base + ".jpg"):
        return path_base + ".jpg"
    if path.exists(path_base + ".jpeg"):
        return path_base + ".jpeg"

    if not "_bubble_gt" in name:
        return get_label(name + "_bubble_gt", labels_base)

    return None


def get_text_gt_path(name, ocr_base):
    path_base = os.path.join(ocr_base, name, name + ".json")

    if path.exists(path_base):
        return path_base
    return None


parser = argparse.ArgumentParser()

parser.add_argument('test_images_dir', type=str, help='path to directory containing source images (comic pages)')
parser.add_argument('results_base_dir', type=str, help='path where results will be saved')
parser.add_argument('masks_base_dir', type=str,
                    help='path to directory containing gt bubble masks, mask file should have the same name as the '
                         'source image')
parser.add_argument('ocr_base_dir', type=str,
                    help='path to directory containing gt ocr, excepted ocr gt structure: ocr_base_dir/name/name.json')

args = parser.parse_args()

dirs = [args.test_images_dir, args.results_base_dir, args.masks_base_dir, args.ocr_base_dir]
for dir in dirs:
    if not os.path.isdir(dir):
        print("Directory does not exist: " + dir)
        exit(1)

logger = ConsoleLogger(verbose_level=Verbosity.INFO)
validate_results(args.test_images_dir, args.results_base_dir, args.masks_base_dir, args.ocr_base_dir, logger)
