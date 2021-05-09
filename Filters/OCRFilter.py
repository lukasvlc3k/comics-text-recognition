from Filters.BubbleFilter import BubbleFilter
from Entities.BubbleCandidate import BubbleCandidate


class OCRFilter(BubbleFilter):
    def __init__(self, source_width, source_height, logger, avg_conf_required=None, ocr_config=None):
        BubbleFilter.__init__(self, "OCR filter", source_width, source_height, logger)

        # using default values if value not provided
        self.avg_conf_required = avg_conf_required if avg_conf_required is not None else 20
        self.ocr_config = ocr_config if ocr_config is not None else {
            "force_use_whitelist": True,
            "tess_config_name": "comics"
        }

    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        ocr_text, ocr_avg_confidence, ocr_max_confidence = bubble_candidate.get_ocr(self.ocr_config)
        text_len = len(ocr_text.strip())

        text_ok = text_len > 0
        if not text_ok:
            self.log_reject_reason(bubble_candidate.component_id, "text length", text_ok, 1)
            return False

        conf_ok = ocr_avg_confidence >= self.avg_conf_required
        if not conf_ok:
            self.log_reject_reason(bubble_candidate.component_id, "avg confidence", ocr_avg_confidence,
                                   self.avg_conf_required)
            return False

        return True
