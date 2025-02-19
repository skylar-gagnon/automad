import time
from modules.parser import Parser
from modules.classifier import Classifier
from modules.generator import Generator
from modules.logger import Logger

classifier = Classifier("arm/pmc_template.c", "configs/measure.xml")
print(classifier.get_results("test"))