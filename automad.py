import time, sys, json
from modules.classifier import Classifier
from modules.generator import Generator
from modules.logger import Logger
from modules.utils import * 

def fuzz(config):
    generator = Generator(config["automad_path"], **config["generator_kwargs"])
    classifier = Classifier(config["automad_path"], train=False, **config["classifier_kwargs"])
    logger = Logger(classifier.flags, config["automad_path"], **config["logger_kwargs"])

    if (config["save_config"]) : logger.save_config(config)

    #! Fuzzing Loop
    stop_time = time.time() + runtime2sec(config["runtime"])
    while time.time() < stop_time:
        responses = generator.generate()
        results = [classifier.get_result(s) for s in responses]
        logger.update(results, responses)

def fuzz_and_train(config):
    generator = Generator(config["automad_path"], **config["generator_kwargs"])
    classifier = Classifier(config["automad_path"], train=True, **config["classifier_kwargs"])
    logger = Logger(classifier.flags, config["automad_path"], **config["logger_kwargs"])

    if (config["save_config"]) : logger.save_config(config)

    generator.train(classifier, logger, **config["train_kwargs"])

def main():
    # Get Config Name
    try:
        automad_config_name = sys.argv[1]
    except Exception:
        automad_config_name = "configs/debug.json"

    # Get key arguments
    with open(automad_config_name, "r") as file:
        config = json.load(file)

    # Begin Fuzzing
    print_launch_msg(config)
    try:
        if config["train"]:
            fuzz_and_train(config)
        else:
            fuzz(config)
        print_exit_msg(0)
    except:
        print_exit_msg(1)
        if config["email_if_fail"]:
            notif_failure("AutoMAD Fuzzing Attempt", sys.exc_info(), f"{config['automad_path']}/{config['email_config_path']}")

if __name__ == "__main__":
    main()