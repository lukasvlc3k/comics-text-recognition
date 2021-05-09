import os.path
import time
import config
from Exceptions import FileReadException
from comics_processing import process_comic_page
from Output.ConsoleLogger import ConsoleLogger, Verbosity
import argparse

if __name__ == "__main__":
    # ===== arguments parsing =====
    # usage: main.py source_img mask_img text_results [-v] [-vl level] [-sb path]

    parser = argparse.ArgumentParser()

    parser.add_argument('source_img', type=str, help='Input comic page path')
    parser.add_argument('mask_img', type=str, help='Output bubble mask path')
    parser.add_argument('text_results', type=str, help='Output JSON results path')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="set verbose level to debug",
                        required=False)

    parser.add_argument('-vl', '--verbose-level',
                        help="set verbose level: 0 = none, 1 = warning, 2 = info, 3 = debug",
                        required=False)

    parser.add_argument('-sb', '--save-bubbles',
                        help="directory where detected bubbles will be saved",
                        required=False)

    args = parser.parse_args()

    verbose_level = 2  # default value
    if args.verbose:  # modified by --verbose
        verbose_level = 3
    if args.verbose_level:  # modified by --verbose-level
        verbose_level = int(args.verbose_level)

    dir_detected_bubbles = None
    if args.save_bubbles:
        if not os.path.isdir(args.save_bubbles):
            print("Invalid directory: " + args.save_bubbles)
            exit(1)

        dir_detected_bubbles = args.save_bubbles

    with open(args.text_results, "w") as f_text:
        try:
            logger = ConsoleLogger(Verbosity(verbose_level))

            start = time.time()
            process_comic_page(args.source_img, args.mask_img, f_text, config=config,
                               parts_directory=dir_detected_bubbles,
                               logger=logger)
            end = time.time()

        except FileNotFoundError:
            print("Input file " + args.source_img + " not found")
        except FileReadException:
            print(
                "Not able to read file " + args.source_img + ". Image format not supported, corrupted or insufficient "
                                                             "permissions for this operation")
        except Exception as e:
            print("An error occured during the processing:\n" + str(e))

    logger.debug("Elapsed time: {time} ms".format(time=(end - start)))
