from Utils.image_utils import mask_image, find_top_contour, fill_contour, get_contour_area, get_perimeter, \
    get_bounding_box, apply_mask
from Utils.ocr_utils import get_ocr_for_bubble_candidate


class BubbleCandidate:
    def __init__(self, component_id, centroid, component_area, component_area_ratio, source_image, canny_image, labels):
        # component info
        self.component_id = component_id
        self.centroid = centroid
        self.component_area = component_area
        self.component_area_ratio = component_area_ratio

        self.source_image = source_image
        self.canny_image = canny_image
        self.labels = labels

        self.was_tested = False
        self.is_bubble = True  # init value

        self.rejected_by = None

        self.component_mask = None
        self.contour = None
        self.bubble_mask_filled = None

        self.masked_source = None
        self.cropped_masked_source = None

        self.hierarchy = None
        self.contours_filled = None

        self.contour_area = None
        self.perimeter = None
        self.bounding_box = None
        self.filters_ok = []

        self.ocr_text = None
        self.ocr_avg_confidence = None
        self.ocr_max_confidence = None

    def reject(self, rejected_by):
        self.rejected_by = rejected_by
        self.is_bubble = False
        self.was_tested = True

        self.component_mask = None
        self.contour = None
        self.bubble_mask_filled = None

    def test_completed(self):
        # self.rejected_by = None
        # self.is_bubble = True
        self.was_tested = True

    def get_component_mask(self):
        if self.component_mask is None:
            self.component_mask = mask_image(self.labels, self.component_id)

        return self.component_mask

    def get_contour(self):
        if self.contour is None:
            self.contour = find_top_contour(self.get_component_mask())

        return self.contour

    def get_bubble_mask_filled(self):
        if self.bubble_mask_filled is None:
            img = self.get_component_mask().copy()
            fill_contour(img, self.get_contour())
            self.bubble_mask_filled = img

        return self.bubble_mask_filled

    def get_contour_area(self):
        if self.contour_area is None:
            self.contour_area = get_contour_area(self.get_contour())

        return self.contour_area

    def get_perimeter(self):
        if self.perimeter is None:
            self.perimeter = get_perimeter(self.get_contour())

        return self.perimeter

    def get_bounding_box(self):
        if self.bounding_box is None:
            self.bounding_box = get_bounding_box(self.get_contour())

        return self.bounding_box

    def get_masked_source(self):
        if self.masked_source is None:
            self.masked_source = apply_mask(self.source_image, self.get_bubble_mask_filled())

        return self.masked_source

    def get_ocr(self, ocr_config):
        if self.ocr_text is None or self.ocr_avg_confidence is None or self.ocr_max_confidence is None:
            if ocr_config is None:
                ocr_config = {
                    "force_use_whitelist": True,
                    "tess_config_name": "comics"
                }
            self.ocr_text, results, self.ocr_max_confidence, self.ocr_avg_confidence = get_ocr_for_bubble_candidate(
                self, ocr_config)
        return self.ocr_text, self.ocr_avg_confidence, self.ocr_max_confidence

    def get_candidate_results(self, ocr_config):
        ocr_text, ocr_avg_confidence, ocr_max_confidence = self.get_ocr(ocr_config)
        x, y, w, h = self.get_bounding_box()
        bounding_box = {"x": x, "y": y, "width": w, "height": h}
        centroid = {"x": self.centroid[0],
                    "y": self.centroid[1]}
        bubble_info = {"id": self.component_id, "area": self.contour_area,
                       "boundingBox": bounding_box,
                       "centroid": centroid}
        ocr = None

        if ocr_text is not None and ocr_text.strip() != "":
            ocr = {"text": ocr_text, "avgConfidence": ocr_avg_confidence, "maxConfidence": ocr_max_confidence}

        return {"bubbleInfo": bubble_info, "ocr": ocr}

    def __str__(self):
        return "[" + str(self.component_id) + "]"
