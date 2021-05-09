filters_parameters = {
                         "component_area_filter": {
                             # filtering based on ratio: (component area (bubble w/o text)) / (full page area)
                             "min_ratio": 0.0005,  # filters out bubble candidates with a ratio less than
                             "max_ratio": 1  # filters out bubble candidates with a ratio greater than
                         },
                         "area_filter": {  # filtering based on ratio: (contour area (filled bubble)) / (full page area)
                             "min_ratio": 0.0005,  # filters out bubble candidates with a ratio less than
                             "max_ratio": 0.05  # filters out bubble candidates with a ratio greater than
                         },
                         "shape_filter": {
                             # filtering based on ratio (component area) / (contour area)
                             "min_ratio_component_area": 0.45,  # filters out bubble candidates with a ratio less than
                             # filtering based on ratio (perimeter) / (contour area)
                             "min_pa_ratio": 0.0075,  # filters out bubble candidates with a ratio less than
                             "max_pa_ratio": 0.15,  # filters out bubble candidates with a ratio greater than
                             # filtering based on ratio (bounding rectangle width/height) / (comic page width/height)
                             "w_min": 0.005,  # filters out bubble candidates with a ratio less than
                             "w_max": 0.6,  # filters out bubble candidates with a ratio greater than
                             "h_min": 0.005,  # filters out bubble candidates with a ratio less than
                             "h_max": 0.6  # filters out bubble candidates with a ratio greater than
                         },
                         "content_filter": {
                             # filtering based on content (black/white pixels changes in a row and a col)
                             "min_changes_row": 6,  # minimum b/w changes required in a pixel row
                             "min_changes_col": 2,  # minimum b/w changes required in a pixel col
                             "required_ratio_row": 0.1,  # required accepted pixel rows of all pixel rows
                             "required_ratio_col": 0.1  # required accepted pixel cols of all pixel cols
                         },
                         "ocr_filter": {  # filtering based on OCR
                             "required_avg_conf": 20  # required average confidence level
                         }
                     },
ocr_config = {
    "force_use_whitelist": True,
    "tess_config_name": "comics"
}


# returns filter parameter from config based on filter name and parameter name
# if config or value not found -> returns None
def get_filter_par(config, filter_name, par_name, logger) -> float or None:
    try:
        filt_par = get_config_value(config, "filters_parameters", logger)
        if filt_par is None or len(filt_par) == 0:
            raise KeyError

        filt_par = filt_par[0]
        if filt_par[filter_name][par_name] is None:
            raise KeyError

        return float(filt_par[filter_name][par_name])
    except KeyError:
        logger.warning("Parameter {par_name} on filter {filter_name} config not found, using default value".format(
            par_name=par_name, filter_name=filter_name))
        return None


def get_config_value(config, key, logger):
    try:
        if config is None:
            raise KeyError

        value = getattr(config, key)
        if value is None:
            raise KeyError

        return value
    except KeyError:
        logger.warning("Config key {key} not found, using default values instead".format(key=key))
    except AttributeError:
        logger.warning("Config key {key} not found, using default values instead".format(key=key))
    return None


if __name__ == "__main__":
    print("This python file can not be run as a script")
