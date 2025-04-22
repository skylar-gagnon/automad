import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from modules.classifier import Classifier
from modules.generator import Generator
from modules.logger import Logger
from modules.utils import * 
import pandas as pd
import time, json

def plot_currents(currs=None):
    if currs is None:
        df = pd.read_csv('data/currents.csv')
        currs = df['currents']

    plt.rc('font', size=28)
    fig, ax = plt.subplots(figsize=(30, 10), facecolor='#d9d9d9')
    ax.yaxis.set_major_locator(ticker.MaxNLocator(1))

    ax.plot(np.arange(0, len(currs) * 1.1, 1.1)[:300], currs[:300], color='#299A3A', linewidth=3)
    ax.set_facecolor("#e9eceb")
    ax.set_xlabel("Time (ms)", labelpad=30)
    ax.set_ylabel("Current (mA)", labelpad=20)
    fig.tight_layout(rect=[0.01, 0.05, 1, 0.95])
    fig.savefig("current.png")

def demo():
    with open(sys.argv[1], "r") as f:
        config = json.load(f)

    start_time = print_launch_msg(config)
    
    generator = Generator(config["automad_path"], **config["generator_kwargs"])
    classifier = Classifier(config["automad_path"], train=False, **config["classifier_kwargs"])
    logger = Logger(start_time, classifier.flags, config["automad_path"], **config["logger_kwargs"])

    if (config["save_config"]) : logger.save_config(config)

    #! Fuzzing Loop
    stop_time = time.time() + runtime2sec(config["runtime"])
    while time.time() < stop_time:
        response = generator.generate()
        results, currs = classifier.demo(response[0])
        if currs is not None: plot_currents(currs=currs)
        logger.update([results], response)

    print_exit_msg(0)

if __name__ == '__main__':
    demo()