class TesseractResultItem:
    def __init__(self, level, line_num, left, top, width, height, conf, text):
        self.level = level
        self.line_num = line_num
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.conf = conf
        self.text = text
