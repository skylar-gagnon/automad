import os
import modules.utils as utils

class Logger:

    #TODO
    def __init__(self, name):
        self.name = name
        
        try:
            os.makedirs(f"logs/{self.name}")
        except FileExistsError:
            utils.throw_error(f"run named {name} already exists")

    #TODO:
    def update(self, results):
        for r in results:
            print(r)