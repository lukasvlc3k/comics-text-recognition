from Filters.BubbleFilter import BubbleFilter
from Entities.BubbleCandidate import BubbleCandidate


class ShapeFilter(BubbleFilter):
    def __init__(self, source_width, source_height, logger, min_ratio_component_area=None, min_pa_ratio=None,
                 max_pa_ratio=None, w_min=None, w_max=None, h_min=None, h_max=None):
        BubbleFilter.__init__(self, "ShapeFilter", source_width, source_height, logger)

        # using default values if value not provided
        self.min_ratio_component_area = min_ratio_component_area if min_ratio_component_area is not None else 0.45
        self.min_pa_ratio = min_pa_ratio if min_pa_ratio is not None else 0.0075
        self.max_pa_ratio = max_pa_ratio if max_pa_ratio is not None else 0.15
        self.w_min = w_min if w_min is not None else 0.005
        self.w_max = w_max if w_max is not None else 0.6
        self.h_min = h_min if h_min is not None else 0.005
        self.h_max = h_max if h_max is not None else 0.6

    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        contour_area = bubble_candidate.get_contour_area()
        perimeter = bubble_candidate.get_perimeter()

        if contour_area == 0:
            self.log_reject_reason(bubble_candidate.component_id, "contour area > 0", 0, 1)
            return False

        ratio_component_area = bubble_candidate.component_area / contour_area
        if ratio_component_area < self.min_ratio_component_area:
            self.log_reject_reason(bubble_candidate.component_id, "component / contour area", ratio_component_area,
                                   self.min_ratio_component_area)

            return False

        pa_ratio = perimeter / contour_area
        if pa_ratio < self.min_pa_ratio:
            self.log_reject_reason(bubble_candidate.component_id, "min perimeter / contour area", pa_ratio,
                                   self.min_pa_ratio)
            return False

        if pa_ratio > self.max_pa_ratio:
            self.log_reject_reason(bubble_candidate.component_id, "max perimeter / contour area", pa_ratio,
                                   self.max_pa_ratio)
            return False

        x, y, w, h = bubble_candidate.get_bounding_box()

        if w < self.source_width * self.w_min:
            self.log_reject_reason(bubble_candidate.component_id, "min width", w,
                                   self.source_width * self.w_min)
            return False
        if w > self.source_width * self.w_max:
            self.log_reject_reason(bubble_candidate.component_id, "max width", w,
                                   self.source_width * self.w_max)
            return False

        if h < self.source_height * self.h_min:
            self.log_reject_reason(bubble_candidate.component_id, "min height", h,
                                   self.source_height * self.h_min)
            return False
        if h > self.source_height * self.h_max:
            self.log_reject_reason(bubble_candidate.component_id, "max height", h,
                                   self.source_height * self.h_max)
            return False

        return True
