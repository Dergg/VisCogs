#!/usr/bin/python3
# Working with the data

import spacy
import pandas as pd
import nltk
import sys # For command line inputs
from nltk.tokenize import WhitespaceTokenizer, sent_tokenize
from alive_progress import alive_bar # I like this progress bar better...
from tqdm import tqdm # ...but this progress bar works better for pandas operations

tqdm.pandas() # Progress bar for pandas stuff.

print("Reading data...")
recordData = pd.read_csv("discogs_data.csv")
print("Done.")
rdq = recordData.query('data_quality != "Needs Major Changes"')
rdq = rdq[rdq['profile'].notnull()] # Filter down the data to stuff we can actually use
rdq['profile'] = rdq['profile'].str.replace(r"\n", " ") # Remove the \n from the profiles so they don't cause any issues.
rdq['all_hyperlinks'] = rdq['profile'].str.extract(r'\[(.*?)\]') # Regex to just get anything within square brackets.
# rdq[['hl_type', 'hyperlink_replace']] = rdq['all_hyperlinks'].str.extract(r'\[(\w+)(?:=([^\]]+))?\]') # Regex to get just names or numbers
# rdq['hl_rep'] = rdq.apply(lambda row: (row['hl_type'], row['all_hyperlinks']), axis=1) # Combine to get a tuple of (artist/label, name)
# print(rdq['hl_rep'].head(3))

wtk = WhitespaceTokenizer()
print("Tokenising profiles...")
rdq['sentences'] = rdq['profile'].progress_apply(lambda x: sent_tokenize(x))
print(rdq['sentences'].values[0])
rdq['profile_tokenised'] = rdq['profile'].progress_apply(lambda x: nltk.word_tokenize(x))
print("Profiles tokenised.")

def process_text(text):
    sentences = sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    return tagged_sentences

print("Tagging sentences...")

# Apply the function to the DataFrame
rdq['tagged_sentences'] = rdq['profile'].progress_apply(process_text)
print("Done.")

rdq['profile_string'] = rdq['profile_tokenised'].apply(lambda x: ' '.join([item for item in x]))
# nltk.download('averaged_perceptron_tagger_eng')
# nltk.download('punkt_tab')
# ^^ Above packages have already been downloaded.
print("Tagging tokens...")
try:
    if sys.argv[1] == "test":
        rdq['tagged_tokens'] = rdq['profile_string'].head(1000).progress_apply(lambda x: nltk.pos_tag(nltk.tokenize.word_tokenize(x)))
    elif sys.argv[1] == "build":
        print("Build mode has been specified. Please be patient, this might take a little while.")
        rdq['tagged_tokens'] = rdq['profile_tokenised'].progress_apply(lambda x: nltk.pos_tag(x))
        rdq.to_csv('processedDiscogs.csv') # Write dataframe to CSV.
        print("Dataframe written to CSV file.")
    else:
        print("You have not specified a tagging method. Please use test or build depending on what you want.")
except Exception as e:
    print(e)
    print("No command specified. Please use 'test' or 'build' when running the program to correctly tag tokens.")
    exit()
print("Done.")
print(rdq.iloc[0]['tagged_tokens']) # Show the head for now. We can build from this later.