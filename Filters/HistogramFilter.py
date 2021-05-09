import numpy as np

from Filters.BubbleFilter import BubbleFilter
from Entities.BubbleCandidate import BubbleCandidate
from Utils.image_utils import to_grayscale


class HistogramFilter(BubbleFilter):
    def __init__(self, source_width, source_height, logger):
        BubbleFilter.__init__(self, "HistogramFilter", source_width, source_height, logger)

    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        masked = bubble_candidate.get_masked_source()
        gray = to_grayscale(masked)

        unique, counts = np.unique(10 * np.round(gray / 10), return_counts=True)
        counts = dict(zip(unique, counts))

        contour_area = bubble_candidate.contour_area

        counts[0] -= ((self.source_width * self.source_height) - contour_area)
        reduced = dict(filter(lambda elem: elem[1] > contour_area / 50, counts.items()))

        colors = list(reduced.keys())

        minimum = np.min(colors)
        maximum = np.max(colors)

        result = (maximum - minimum) > 70

        if not result:
            self.log_reject_reason(bubble_candidate.component_id, "contract", (maximum - minimum), 70)

        return result
