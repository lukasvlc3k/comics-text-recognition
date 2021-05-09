from Entities.BubbleCandidate import BubbleCandidate
from Filters.BubbleFilter import BubbleFilter
from Utils.image_utils import apply_mask


class ContentFilter(BubbleFilter):
    def __init__(self, source_width, source_height, logger, min_changes_row=None, min_changes_col=None,
                 required_ratio_row=None, required_ratio_col=None):
        BubbleFilter.__init__(self, "ContentFilter", source_width, source_height, logger)

        # using default values if value not provided
        self.min_changes_row = min_changes_row if min_changes_row is not None else 6
        self.min_changes_col = min_changes_col if min_changes_col is not None else 2
        self.required_ratio_row = required_ratio_row if required_ratio_row is not None else 0.1
        self.required_ratio_col = required_ratio_col if required_ratio_col is not None else 0.1

    def is_accepted(self, bubble_candidate: BubbleCandidate) -> bool:
        masked = apply_mask(bubble_candidate.canny_image, bubble_candidate.get_bubble_mask_filled())

        x, y, w, h = bubble_candidate.get_bounding_box()

        zc_count_row = 0
        nzc_count_row = 0

        zc_count_col = 0
        nzc_count_col = 0

        for row in range(y, y + h):
            changes_count = count_changes(masked, row, row + 1, x, x + w)
            if changes_count >= self.min_changes_row:
                nzc_count_row += 1
            else:
                zc_count_row += 1

        for column in range(x, x + w):
            changes_count = count_changes(masked, y, y + h, column, column + 1)
            if changes_count >= self.min_changes_col:
                nzc_count_col += 1
            else:
                zc_count_col += 1

        rows_ratio = nzc_count_row / (nzc_count_row + zc_count_row)
        rows_ratio_ok = rows_ratio >= self.required_ratio_row
        if not rows_ratio_ok:
            self.log_reject_reason(bubble_candidate.component_id, "rows ok ratio", rows_ratio, self.required_ratio_row)
            return False

        cols_ratio = nzc_count_col / (nzc_count_col + zc_count_col)
        cols_ratio_ok = cols_ratio >= self.required_ratio_col
        if not cols_ratio_ok:
            self.log_reject_reason(bubble_candidate.component_id, "cols ok ratio", cols_ratio, self.required_ratio_col)
            return False

        return True


def count_changes(masked, row_start, row_end, column_start, column_end) -> int:
    last_color = 0
    ok_changes = 0
    last_color_length = 0

    minimum_color_length = 1
    maximum_color_length = 50000

    for row in range(row_start, row_end):
        for column in range(column_start, column_end):
            pixel_color = masked[row, column]
            if pixel_color != last_color:
                last_color = pixel_color
                if minimum_color_length < last_color_length < maximum_color_length:
                    ok_changes += 1
            else:
                last_color_length += 1

    return ok_changes
