from Entities.BubbleCandidate import BubbleCandidate
from Filters.BubbleFilter import BubbleFilter


class ComponentAreaFilter(BubbleFilter):
    def __init__(self, source_width, source_height, logger, min_ratio=None, max_ratio=None):
        BubbleFilter.__init__(self, "ComponentAreaFilter", source_width, source_height, logger)

        # using default values if value not provided
        self.min_ratio = min_ratio if min_ratio is not None else 0.0005
        self.max_ratio = max_ratio if max_ratio is not None else 1

    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        component_area_ratio = bubble_candidate.component_area_ratio

        min_ok = component_area_ratio >= self.min_ratio
        if not min_ok:
            self.log_reject_reason(bubble_candidate.component_id, "min ratio", component_area_ratio, self.min_ratio)
            return False

        max_ok = component_area_ratio <= self.max_ratio
        if not max_ok:
            self.log_reject_reason(bubble_candidate.component_id, "max ratio", component_area_ratio, self.max_ratio)
            return False

        return self.min_ratio <= component_area_ratio <= self.max_ratio
