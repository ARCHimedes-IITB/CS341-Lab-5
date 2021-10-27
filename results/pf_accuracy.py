from collections import defaultdict
import json
from os import listdir
from os.path import isfile, join
from tabulate import tabulate
import pandas as pd

def readValues(file):    
    accuracies = defaultdict(float)
    ipcs = defaultdict(float)
    coverage = defaultdict(float)
    misses = defaultdict(float)

    with open(file, 'r') as f:
        for line in f:
            if line.startswith('L1D PREFETCH  REQUESTED') or line.startswith('L2C PREFETCH  REQUESTED'):
                l = line.split()
                try:
                    accuracies[l[0]] = float(l[-3]) / (float(l[-3]) + float(l[-1]))
                except:
                    accuracies[l[0]] = float("nan")
                try:
                    coverage[l[0]] = float(l[-3]) / (float(l[-3]) + misses[l[0]])
                except:
                    coverage[l[0]] = float("nan")
            elif line.startswith('CPU 0 cumulative IPC:'):
                l = line.split()
                ipcs["Cumulative IPC"] = float(l[4])
            elif ('LOAD      ACCESS' in line or 'RFO       ACCESS' in line) and ('L1D' in line or 'L2C' in line):
                l = line.split()
                misses[l[0]] += float(l[-1])

    return accuracies, ipcs, coverage

def findAccuracies(path, accuracies, ipcs, coverage):
    for f in listdir(path):
        cur_path = join(path, f)
        if isfile(cur_path):
            if f.endswith('.txt'):
                accuracies[f], ipcs[f], coverage[f] = readValues(cur_path)
        else:
            findAccuracies(cur_path, accuracies, ipcs, coverage)

def flipDict(d):
    flipped = defaultdict(lambda: defaultdict(float))

    for key, val in d.items():
        for subkey, subval in val.items():
            flipped[subkey][key] = subval
    
    return flipped

def colorize(d):
    maxv = defaultdict(float)
    maxi = defaultdict(int)

    for key, val in d.items():
        for subkey, subval in val.items():
            if subval > maxv[key]:
                maxv[key] = subval
                maxi[key] = subkey

    for key, val in d.items():
        d[key][maxi[key]] = '\u001b[31m\033[1m' + str(val[maxi[key]]) + '\033[0m\u001b[0m'
    
    return d

if __name__ == '__main__':
    accuracies = defaultdict(lambda: defaultdict(float))
    ipcs = defaultdict(lambda: defaultdict(float))
    coverage = defaultdict(lambda: defaultdict(float))

    findAccuracies(".", accuracies, ipcs, coverage)

    accuracies = flipDict(accuracies)
    ipcs = flipDict(ipcs)
    coverage = flipDict(coverage)

    print(accuracies)

    with open('accuracies.json', 'w') as f:
        json.dump(accuracies, f, indent = 4)
    with open('ipcs.json', 'w') as f:
        json.dump(ipcs, f, indent = 4)
    with open('coverage.json', 'w') as f:
        json.dump(coverage, f, indent = 4)

    table = pd.DataFrame(colorize(ipcs))
    print("\n"+"-"*22+"IPCs"+"-"*22+"\n", tabulate(table, headers='keys', tablefmt='psql'))
    table = pd.DataFrame(colorize(coverage))
    print("\n"+"-"*23+"Coverage"+"-"*23+"\n", tabulate(table, headers='keys', tablefmt='psql'))
    table = pd.DataFrame(colorize(accuracies))
    print("\n"+"-"*23+"Accuracy"+"-"*23+"\n", tabulate(table, headers='keys', tablefmt='psql'))