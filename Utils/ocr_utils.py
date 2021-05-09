from pytesseract import pytesseract, Output
from Entities.TesseractResultItem import TesseractResultItem

def get_ocr_for_bubble_candidate(bubble_candidate, ocr_config):
    x, y, w, h = bubble_candidate.get_bounding_box()
    masked = bubble_candidate.get_masked_source()

    bubble_mask_inverted = 255 - bubble_candidate.get_bubble_mask_filled()
    masked[bubble_mask_inverted == 255] = (255, 255, 255)

    masked_cropped = masked[y:y + h, x:x + w]

    return get_ocr(masked_cropped, ocr_config)


def get_ocr(image, ocr_config):
    ocr_part_results = []

    ocr_part_results.append(__get_ocr(image, True, ocr_config))
    if not ocr_config["force_use_whitelist"]:
        ocr_part_results.append(__get_ocr(image, False, ocr_config))

    best_res = None

    for part_res in ocr_part_results:
        if best_res is None or part_res[3] > best_res[3]:
            best_res = part_res

    return best_res[0], best_res[1], best_res[2], best_res[3]


def __get_ocr(image, use_whitelist, ocr_config):
    config = "--psm 3"
    if use_whitelist:
        config += " " + ocr_config["tess_config_name"]
    ocr_text = pytesseract.image_to_string(image, config=config).strip()
    ocr_results_dict = pytesseract.image_to_data(image,
                                                 config=config,
                                                 output_type=Output.DICT)

    tess_results = []

    entries_count = len(ocr_results_dict["text"])

    max_conf = -100
    conf_sum = 0
    conf_count = 0

    for i in range(entries_count):
        level = ocr_results_dict["level"][i]
        page_num = ocr_results_dict["page_num"][i]
        block_num = ocr_results_dict["block_num"][i]
        par_num = ocr_results_dict["par_num"][i]
        line_num = ocr_results_dict["line_num"][i]
        word_num = ocr_results_dict["word_num"][i]
        left = ocr_results_dict["left"][i]
        top = ocr_results_dict["top"][i]
        width = ocr_results_dict["width"][i]
        height = ocr_results_dict["height"][i]
        conf = ocr_results_dict["conf"][i]
        text = ocr_results_dict["text"][i]

        conf_i = int(conf)
        if conf_i > max_conf:
            max_conf = conf_i

        if conf_i != -1:
            conf_sum += conf_i * len(text)
            conf_count += len(text)

        tess_results.append(TesseractResultItem(level, line_num, left, top, width, height, conf, text))

    avg_conf = conf_sum / conf_count if conf_count > 0 else 0

    return ocr_text, tess_results, max_conf, avg_conf
