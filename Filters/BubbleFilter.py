from abc import abstractmethod

from Entities.BubbleCandidate import BubbleCandidate


# base class used for all bubble candidate filters
class BubbleFilter:
    def __init__(self, name, source_width, source_height, logger):
        self.name = name
        self.logger = logger

        # dimensions of the source image (comic page)
        self.source_width = source_width
        self.source_height = source_height

    @abstractmethod
    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        return True
        # method determining whether or not a bubble candidate matches a given filter

    def log_reject_reason(self, candidate_id, test_name, value, required):
        self.logger.debug(
            "\t[{candidate_id}] rejected by {filter_name}:{test_name} (value: {value}, required: {required})".format(
                candidate_id=candidate_id, filter_name=self.name, test_name=test_name, value=value, required=required))
