# define Python user-defined exceptions
class Error(Exception):
    """Base class for all exceptions"""
    pass


class FileReadException(Error):
    """Raised reading file error occurred"""
    pass


if __name__ == "__main__":
    print("This python file can not be run as a script")
