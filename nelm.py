#!/usr/bin/python3
# Node & Edge List Maker Program
# Take things from the processed and tagged Discogs data.

import sys
import pandas as pd
import nltk
from tqdm import tqdm
from nltk.tokenize import sent_tokenize

tqdm.pandas()

print("Reading data...")
data = pd.read_csv('processedDiscogs.csv')
print("Complete.")

try:
    if sys.argv[1] == 'node':
        print("WIP")
    elif sys.argv[1] == 'edge':
        print("WIP")
    else:
        print("Please specify if you want to make an edge or a node list.")

except:
    print("Please specify if you want to make a node or edge list using 'node' or 'edge' after calling program.")
    exit()