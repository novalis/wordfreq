#!/usr/bin/python

import os, sys
from bintrees import RBTree


resultfile = sys.argv[1]
COUNT = 2**23

biggest = RBTree()
if os.path.exists(resultfile):
    with open(resultfile) as f:
        for line in f:
            word, count = line.split('\t')
            count = int(count)
            biggest.insert((count, word), 1)

    for count, word in biggest.keys():
        threshold = count
        break

else:
    threshold = 0

ngramfile = sys.argv[2]
with open(ngramfile) as f:
    last_gram = None
    total_count = 0
    for line in f:
        if '_' in line:
            continue
        if ')' in line:
            continue
        if '(' in line:
            continue
        if '[' in line:
            continue
        if ']' in line:
            continue
        if ',' in line:
            continue
        gram, year, match_count, volume_count = line.split('\t')
        match_count = int(match_count)
        if gram == last_gram:
            total_count += match_count
        else:
            if total_count > threshold:
                biggest.insert((total_count, last_gram.strip()), 1)
                if len(biggest) == COUNT:
                    threshold = biggest.pop_min()[0][0]
            total_count = match_count
            last_gram = gram

if total_count > threshold:
    biggest.insert((total_count, last_gram.strip()), 1)
    if len(biggest) == COUNT:
        biggest.pop_min()

with open(resultfile + ".lock", 'w') as f:
    for count, word in biggest.keys():
        f.write(word + "\t" + str(count) + "\n")


os.rename(resultfile + ".lock", resultfile)
