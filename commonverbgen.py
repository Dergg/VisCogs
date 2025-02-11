import spacy
import pandas as pd
import nltk
import sys # For command line inputs
from nltk.tokenize import WhitespaceTokenizer, sent_tokenize
from alive_progress import alive_bar # I like this progress bar better...
from tqdm import tqdm # ...but this progress bar works better for pandas operations

# Counting out the verbs for empirical evidence
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer

rdq = pd.read_csv('processedDiscogs.csv')

def extract_verbs(tokens):
    altokens = eval(tokens)
    if not isinstance(altokens, list):
        return []
    return [token for token, tag in altokens if tag.startswith("VB")]

rdq['verbs'] = rdq['tagged_tokens'].apply(lambda x: extract_verbs(x))
all_verbs = [verb for verbs in rdq['verbs'] for verb in verbs]
for i in range(len(all_verbs)):
    all_verbs[i] = all_verbs[i].lower()
    all_verbs[i] = WordNetLemmatizer().lemmatize(all_verbs[i], 'v')
    
verb_counts = Counter(all_verbs)

sorted_verb_counts = sorted(verb_counts.items(), key=lambda x: x[1], reverse=True)
print(sorted_verb_counts[0])

with open('./txts/verb_counts.txt', 'w') as f:
    print(sorted_verb_counts, file=f)

print("Most common verbs now outputted to a text file.")