from collections import defaultdict
import json
from os import listdir
from os.path import isfile, join
from tabulate import tabulate
import pandas as pd

def readValues(file):    
    accuracies = defaultdict(float)

    with open(file, 'r') as f:
        for line in f:
            if line.startswith('L1D PREFETCH  REQUESTED') or line.startswith('L2C PREFETCH  REQUESTED'):
                l = line.split()
                try:
                    accuracies[l[0]] = float(l[-3]) / (float(l[-3]) + float(l[-1]))
                except:
                    accuracies[l[0]] = float("nan")

    return accuracies

def findAccuracies(path, accuracies):
    for f in listdir(path):
        cur_path = join(path, f)
        if isfile(cur_path):
            if f.endswith('.txt'):
                accuracies[cur_path] = readValues(cur_path)
        else:
            findAccuracies(cur_path, accuracies)


if __name__ == '__main__':
    accuracies = defaultdict(lambda: defaultdict(float))
    findAccuracies(".", accuracies)

    flipped = defaultdict(lambda: defaultdict(float))
    for key, val in accuracies.items():
        for subkey, subval in val.items():
            flipped[subkey][key] = subval

    with open('accuracies.json', 'w') as f:
        json.dump(flipped, f, indent = 4)

    table = pd.DataFrame(flipped)
    print(tabulate(table, headers='keys', tablefmt='psql'))