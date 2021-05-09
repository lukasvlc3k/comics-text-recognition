import os
import shutil


def delete_all_files_from_directory(directory):
    for dir_item_name in os.listdir(directory):
        path = os.path.join(directory, dir_item_name)
        try:
            if os.path.isfile(path) or os.path.islink(path):  # is file
                os.unlink(path)
            elif os.path.isdir(path):  # is directory
                shutil.rmtree(path)
        except Exception as e:
            print("Failed to delete %s. Reason %s" % (path, e))


def make_empty_directory(directory_path):
    if os.path.isdir(directory_path):
        delete_all_files_from_directory(directory_path)
    else:
        os.mkdir(directory_path)
