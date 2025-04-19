import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from modules.classifier import Classifier
from modules.logger import Logger
from modules.utils import * 
import pandas as pd

def plot_currents():
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

def get_avg():
    with open('curr2_log', 'r') as f:
        readings = f.read()
    currs = [int(r) for r in readings if r.strip()]

    p2ps = []
    prev_curr = currs[0]
    for curr in currs[1:]:
        p2ps.append(abs(prev_curr - curr))
        prev_curr = curr

    print(float(sum(p2ps)) / len(p2ps))

def demo():
    with open("configs/debug.json", "r") as f:
        config = json.load(f)

    start_time = print_launch_msg(config)
    classifier = Classifier(config["automad_path"], train=False, **config["classifier_kwargs"])
    logger = Logger(start_time, classifier.flags, config["automad_path"], **config
    ["logger_kwargs"])

    snippet_path = "logs/best_avg_12/samples/sample380_5.576880583535788"
    with open(snippet_path, "r") as f:
        s = f.read()

    results = classifier.demo(s)
    logger.update(results, s)

    print_exit_msg(0)

def main():
    if sys.argv[1] == 'plot':
        plot_currents()
    elif sys.argv[1] == 'avg':
        get_avg()
    else:
        demo()

if __name__ == '__main__':
    main()