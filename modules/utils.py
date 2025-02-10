import sys

def throw_error(err_msg):
        sys.stderr.write("Error: " + err_msg)
        exit()

class Result:
    def __init__(self):
        self.parallel = None
        self.serial = None
        self.flags = None