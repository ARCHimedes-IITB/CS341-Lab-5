FOLDER = 'new_prefetch_throttling_result'
CACHES = ['L1D', 'L2C', 'combined']
PLOT_DIR = 'plots'
DATA_DIR = 'data'

BASELINE = {
    'L1D' : {
        'Accuracy': 0.7075658398336128,
        'Coverage': 0.24766700213041262,
        'IPC': 0.21318
    },
    'L2C' : {
        'Accuracy': 0.172458300820783,
        'Coverage': 0.1577135866897137,
        'IPC': 0.21318
    }
}

COLORS = [
    '#B2182B',
    '#EF8A62',
    '#FEDBC7',
    '#D2E5F0',
    '#67A9CF',
    '#2166AC'
]

from collections import defaultdict
import json
from os import listdir
from os.path import isfile, join
from tabulate import tabulate
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import copy

Path(PLOT_DIR).mkdir(exist_ok=True)
Path(DATA_DIR).mkdir(exist_ok=True)

def readValues(file, cache):    
    misses = 0

    with open(file, 'r') as f:
        for line in f:
            if line.startswith(f'{cache} PREFETCH  REQUESTED'):
                l = line.split()
                try:
                    accuracy = float(l[-3]) / (float(l[-3]) + float(l[-1]))
                except:
                    accuracy = float("nan")
                try:
                    coverage = float(l[-3]) / (float(l[-3]) + misses)
                except:
                    coverage = float("nan")
            elif line.startswith('CPU 0 cumulative IPC:'):
                l = line.split()
                ipc = float(l[4])
            elif ('LOAD      ACCESS' in line or 'RFO       ACCESS' in line) and (cache in line):
                l = line.split()
                misses += float(l[-1])

    return accuracy, coverage, ipc

def findAccuracies(cache, accuracies, coverage, ipcs):
    path = join(FOLDER, cache)
    for f in listdir(path):
        cur_path = join(path, f)
        if isfile(cur_path):
            if f.endswith('.txt'):
                accuracies[f[:-4]], coverage[f[:-4]], ipcs[f[:-4]] = readValues(cur_path, cache)


def colorize(d):
    maxv = defaultdict(float)
    maxi = defaultdict(int)

    d2 = copy.deepcopy(d)

    for key, val in d.items():
        for subkey, subval in val.items():
            if subval > maxv[key]:
                maxv[key] = subval
                maxi[key] = subkey

    for key, val in d.items():
        d2[key][maxi[key]] = '\u001b[31m\033[1m' + str(val[maxi[key]]) + '\033[0m\u001b[0m'
    
    return d2

for cache in CACHES:
    accuracies = defaultdict(float)
    coverage = defaultdict(float)
    ipcs = defaultdict(float)

    findAccuracies(cache, accuracies, coverage, ipcs)

    d = {"Accuracy": accuracies, "Coverage": coverage, "IPC": ipcs}

    with open(join(DATA_DIR, f'{cache}.json'), 'w') as f:
        json.dump(d, f, indent = 4)

    table = pd.DataFrame(colorize(d))
    print("\n"+"-"*22+cache+"-"*22+"\n", tabulate(table, headers='keys', tablefmt='psql'))

    # PLOTTING
    files = list(accuracies.keys())

    X = np.arange(len(files))

    data = np.zeros((3, len(files)), dtype=float)
    
    LABELS = ['Accuracy', 'Coverage', 'IPC']
    for i, d2 in enumerate(d.values()):
        for j, file in enumerate(files):
            data[i, j] = 100.0 * (d2[file] / BASELINE[cache][LABELS[i]] - 1)

    plt.figure()
    
    for i in range(data.shape[0]):
        plt.bar(X + i * 0.2, data[i, :], width = 0.2, color = COLORS[i], align='edge', label=LABELS[i])

    plt.ylabel('Percent improvement w.r.t. baseline')
    plt.title(f'Accuracy, Coverage and IPC for {cache} cache')
    plt.xticks(X+0.3, files, rotation=30)
    plt.legend(labels=LABELS)
    plt.grid(linestyle='dotted', linewidth=1)
    # plt.show()
    plt.savefig(f'{PLOT_DIR}/{cache}.png')
   