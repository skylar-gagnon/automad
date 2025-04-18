# import sys, json
import matplotlib.pyplot as plt
import numpy as np
from modules.classifier import Classifier
from modules.utils import * 

def plot_p2p(p2ps):
    plt.rc('font', size=28)
    fig, ax = plt.subplots(figsize=(15, 15), facecolor='#d6d6d6', layout='constrained')

    ax.plot(np.arange(0, len(p2ps) * 1.1, 1.1), p2ps, color='#299A3A')
    ax.set_facecolor("#e9eceb")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Current (mA)")
    # Adjust layout
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    fig.savefig("p2ps.png")


def main():
    with open("configs/debug.json", "r") as f:
        config = json.load(f)

    classifier = Classifier(config["automad_path"], train=False, **config["classifier_kwargs"])
    snippet_path = sys.argv[1]
    with open(snippet_path, "r") as f:
        s = f.read()

    results = classifier.demo()

    plot_p2p(results['p2ps'])

if __name__ == '__main__':
    main()