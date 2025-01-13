#!/usr/bin/python3
# Node & Edge List Maker Program
# Take things from the processed and tagged Discogs data.

import sys
from ast import literal_eval
import pandas as pd
import nltk
from tqdm import tqdm
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tree import Tree
from nltk.chunk import ne_chunk

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# Above packages have been downloaded already.

tqdm.pandas()

print("Reading data...")
data = pd.read_csv('processedDiscogs.csv')
print("Complete.")

def find_fullstop(sentence):
    print(f'Full sentence: {sentence}')
    for i in range(len(sentence)):
        if sentence[i][0] == '.':
            print(f'Found fullstop at index {i}')
            return i

    for context in surrounding_context:
        print(f'Surrounding context length: {len(surrounding_context)}\nContext: {context}')

try:
    if sys.argv[1] == 'node':
        nodelist = []
        print("WIP") # Find dates of when labels were founded
        for i in range(data.shape[0]):
            labelList = [] # Format: Label ID, label name, parent label name (if applicable)
            labelList.append(data['id'].values[i]) # ID
            labelList.append(data['name'].values[i]) # Label name
            if pd.isna(data['parent_name'].values[i]): # If no parent
                labelList.append("n/a") # Append n/a (not applicable)
            else:
                labelList.append(data['parent_name'].values[i]) # Otherwise add it

    elif sys.argv[1] == 'edge':
        print("WIP")
    elif sys.argv[1] == 'experiment':
        print("Please be aware that experimentation can cause severe brain messery.")
        target_words = ["founded", "formed"]
        surrounding_context = []
        scfull = False
        for tagged_sentence in data['tagged_sentences']:
            ts = literal_eval(tagged_sentence) # Convert into list as it is a string for some reason
            if scfull == True:
                break
            for i, (word, tag) in enumerate(ts[0]):
                if scfull == True:
                    break
                if word.lower() in target_words and scfull == False:
                    context = ts[0][max(0, i-3):find_fullstop(ts[0])]
                    print(f'Found word: {word}\n Context: {context}')
                    surrounding_context.append((context, data.at[i, 'name']))
                    if len(surrounding_context) >= 10:
                        scfull = True
                        break
        
        print(f'Found {len(surrounding_context)} different sentences.')

        for context in surrounding_context:
            print(context)

        # Pattern matching goes here, make sure you account for format (word, tag)
    else:
        print("Please specify if you want to make an edge or a node list.")

except:
    print("Please specify if you want to make a node or edge list using 'node' or 'edge' after calling program.")
    exit()