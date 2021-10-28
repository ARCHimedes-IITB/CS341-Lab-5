PLOT_DIR = './plots'
DATA_DIR = './data'

COLORS = [
    '#B2182B',
    '#EF8A62',
    '#FEDBC7',
    '#D2E5F0',
    '#67A9CF',
    '#2166AC'
]
# COLORS.reverse()
LABELS = [
    "Accuracy",
    "Coverage"
]
CACHES = [
    "L1D",
    "L2C"
]
BASELINE = "baseline-prefetcher.txt"

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
from pf_accuracy import *

## CHANGE HERE TO READ FROM JSON FILES

accuracies, ipcs, coverage = main()
# accuracies = json.load(open("accuracies.json", "r"))
# ipcs = json.load(open("ipcs.json", "r"))
# coverage = json.load(open("coverage.json", "r"))

Path(PLOT_DIR).mkdir(exist_ok=True)

def sel(f):
    return f.count("-") == 2 and "no" not in f

for cache_type in CACHES:
    files = list(accuracies[cache_type].keys())
    files = [f for f in files if sel(f)]
    # files is a list of file names which we want to plot

    X = np.arange(len(files))

    data = np.zeros((2, len(files)), dtype=float)
    
    i = 0
    for d in [accuracies, coverage]:
        j = 0
        for file in files:
            data[i, j] = 100.0 * (d[cache_type][file] / d[cache_type][BASELINE] - 1)
            j += 1
        i += 1

    plt.figure()
    
    for i in range(data.shape[0]):
        plt.bar(X + i * 0.3, data[i, :], width = 0.3, color = COLORS[i], align='edge', label=LABELS[i])

    plt.ylabel('Percent improvement w.r.t. baseline')
    plt.title(f'Accuracy and Coverage for {cache_type} cache')
    plt.xticks(X+0.3, [s[:-4] for s in files], rotation=30)
    plt.legend(labels=LABELS)
    plt.grid(linestyle='dotted', linewidth=1)
    # plt.show()
    plt.savefig(f'{PLOT_DIR}/ac_{cache_type}.png')

