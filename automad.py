import time
from modules.parser import Parser
from modules.classifier import Classifier
from modules.generator import Generator
from modules.logger import Logger

#! Initialization
parser = Parser()

generator = Generator(parser.model_name)
classifier = Classifier(parser.config_name)
logger = Logger(parser.run_name)
timeout = time.time() + parser.truetime

#! Fuzzing Loop
parser.print_launch_msg()
while time.time() < timeout:
    snippets = generator.generate()
    results = classifier.check(snippets)
    logger.update(results)
