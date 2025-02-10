import time
from modules.general import Parser
from modules.classifier import Classifier
from modules.generator import Generator
from modules.logger import Logger

classifier = Classifier("configs/measure.xml")
classifier.cleanup()