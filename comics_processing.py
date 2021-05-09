import os

import numpy as np
import json
import cv2

from Entities.BubbleCandidate import BubbleCandidate
from Filters.AreaFilter import AreaFilter
from Filters.HistogramFilter import HistogramFilter
from Filters.ComponentAreaFilter import ComponentAreaFilter
from Filters.ShapeFilter import ShapeFilter
from Filters.OCRFilter import OCRFilter
from Filters.ContentFilter import ContentFilter
from Utils.progress_bar import print_progress_bar
from Utils.fs_utils import make_empty_directory
from Utils.component_detection import get_components
from Utils.image_utils import inverse_single_channel, get_width_height, canny_edge, dilate, save_image, load_image, \
    add_candidate_to_final_mask
from Output.ConsoleLogger import ConsoleLogger, Verbosity


# main function handling processing comic page, saving final bubble mask and result json file
def process_comic_page(input_file, bubble_mask_output_path, results_file, config, logger: ConsoleLogger,
                       parts_directory=None):
    if parts_directory is not None:
        make_empty_directory(parts_directory)

    logger.info("Processing " + input_file + "...")

    # loading input file
    src = load_image(input_file)
    width, height = get_width_height(src)

    # preprocessing
    canny = canny_edge(src, 100, 200)
    dilated = dilate(canny, cv2.MORPH_ELLIPSE, 3)
    inverted = inverse_single_channel(dilated)

    # bubble candidates creating
    bubble_candidates = find_bubble_candidates(inverted, src, canny)

    candidates_filters = init_candidate_filters(config, width, height, logger)

    final_bubble_mask = np.zeros((height, width, 1), np.uint8)  # initialising mask containing all bubbles
    final_results = []

    ocr_config = config.get_config_value(config, "ocr_config", logger)
    done = 0
    for bubble_candidate in bubble_candidates:
        done += 1

        if done % 10 == 0 and logger.verbose_level.value <= Verbosity.INFO.value:
            print_progress_bar(done, len(bubble_candidates), "Processing", "Completed")

        for candidate_filter in candidates_filters:
            filter_accepted = candidate_filter.is_accepted(bubble_candidate)

            if not filter_accepted:
                bubble_candidate.reject(candidate_filter)
                break
            else:
                bubble_candidate.filters_ok.append(candidate_filter)

        bubble_candidate.test_completed()

    print_progress_bar(len(bubble_candidates), len(bubble_candidates), "Processing", "Completed")
    successful_bubble_candidates = [candidate for candidate in bubble_candidates if candidate.is_bubble]

    for bubble_candidate in successful_bubble_candidates:
        if is_candidate_containing_other(bubble_candidate, successful_bubble_candidates):
            print(str(bubble_candidate.component_id) + " inside other")
            bubble_candidate.is_bubble = False
            continue

        if parts_directory is not None:
            save_image(os.path.join(parts_directory, str(bubble_candidate.component_id) + ".png"),
                       bubble_candidate.get_component_mask())
            save_image(os.path.join(parts_directory, str(bubble_candidate.component_id) + "-masked.png"),
                       bubble_candidate.get_masked_source())

        add_candidate_to_final_mask(final_bubble_mask, bubble_candidate)

        candidate_results = bubble_candidate.get_candidate_results(ocr_config)
        final_results.append(candidate_results)

    results_file.write(json.dumps(final_results))
    save_image(bubble_mask_output_path, final_bubble_mask)

    logger.info("Done")


def init_candidate_filters(config, source_image_width, source_image_height, logger):
    component_area_filter = ComponentAreaFilter(source_image_width, source_image_height, logger,
                                                min_ratio=config.get_filter_par(config, "component_area_filter",
                                                                                "min_ratio", logger),
                                                max_ratio=config.get_filter_par(config, "component_area_filter",
                                                                                "max_ratio", logger))
    area_filter = AreaFilter(source_image_width, source_image_height, logger,
                             min_ratio=config.get_filter_par(config, "area_filter", "min_ratio", logger),
                             max_ratio=config.get_filter_par(config, "area_filter", "max_ratio", logger))

    shape_filter = ShapeFilter(source_image_width, source_image_height, logger,
                               min_ratio_component_area=config.get_filter_par(config, "shape_filter",
                                                                              "min_ratio_component_area", logger),
                               min_pa_ratio=config.get_filter_par(config, "shape_filter", "min_pa_ratio", logger),
                               max_pa_ratio=config.get_filter_par(config, "shape_filter", "max_pa_ratio", logger),
                               w_min=config.get_filter_par(config, "shape_filter", "w_min", logger),
                               w_max=config.get_filter_par(config, "shape_filter", "w_max", logger),
                               h_min=config.get_filter_par(config, "shape_filter", "h_min", logger),
                               h_max=config.get_filter_par(config, "shape_filter", "h_max", logger))
    content_filter = ContentFilter(source_image_width, source_image_height, logger,
                                   min_changes_row=config.get_filter_par(config, "content_filter", "min_changes_row",
                                                                         logger),
                                   min_changes_col=config.get_filter_par(config, "content_filter", "min_changes_col",
                                                                         logger),
                                   required_ratio_row=config.get_filter_par(config, "content_filter",
                                                                            "required_ratio_row", logger),
                                   required_ratio_col=config.get_filter_par(config, "content_filter",
                                                                            "required_ratio_col", logger))
    histogram_filter = HistogramFilter(source_image_width, source_image_height, logger)

    ocr_config = config.get_config_value(config, "ocr_config", logger)
    ocr_filter = OCRFilter(source_image_width, source_image_height, logger,
                           avg_conf_required=config.get_filter_par(config, "ocr_filter", "required_avg_conf", logger),
                           ocr_config=ocr_config)

    return [component_area_filter, area_filter, shape_filter, content_filter, histogram_filter,
            ocr_filter]


def find_bubble_candidates(inverted, src, canny):
    # connected components
    num_labels, labels, stats, centroids = get_components(inverted)
    full_size = src.shape[0] * src.shape[1]

    bubble_candidates = []
    for lbl in range(1, num_labels):
        area = stats[lbl, cv2.CC_STAT_AREA]

        if area > 0:
            ratio = area / full_size
            bubble_candidate = BubbleCandidate(lbl, (centroids[lbl, 0], centroids[lbl, 1]), area, ratio, src, canny,
                                               labels)
            bubble_candidates.append(bubble_candidate)

    return bubble_candidates


def is_candidate_containing_other(candidate, all_candidates):
    for other_candidate in all_candidates:
        if candidate.component_id == other_candidate.component_id:
            continue

        intersect = cv2.bitwise_and(candidate.get_bubble_mask_filled(),
                                    other_candidate.get_bubble_mask_filled())
        intersect_size = np.sum(intersect)
        inside_size = np.sum(other_candidate.get_bubble_mask_filled())

        if intersect_size == inside_size:
            if np.sum(other_candidate.get_bubble_mask_filled()) > 0:
                return True
    return False


if __name__ == "__main__":
    print("This python file can not be run as a script")
