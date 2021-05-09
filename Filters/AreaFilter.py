from Entities.BubbleCandidate import BubbleCandidate
from Filters.BubbleFilter import BubbleFilter


# filter filtering out bubble candidates that are too small or too big (according to area ratio)
class AreaFilter(BubbleFilter):
    def __init__(self, source_width, source_height, logger, min_ratio=None, max_ratio=None):
        BubbleFilter.__init__(self, "AreaFilter", source_width, source_height, logger)
        # using default values if value not provided
        self.min_ratio = min_ratio if min_ratio is not None else 0.0005
        self.max_ratio = max_ratio if max_ratio is not None else 0.05

    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        area_ratio = bubble_candidate.get_contour_area() / (self.source_width * self.source_height)

        min_ok = area_ratio >= self.min_ratio
        if not min_ok:
            self.log_reject_reason(bubble_candidate.component_id, "min ratio", area_ratio, self.min_ratio)
            return False

        max_ok = area_ratio <= self.max_ratio
        if not max_ok:
            self.log_reject_reason(bubble_candidate.component_id, "max ratio", area_ratio, self.max_ratio)
            return False

        return True
