#!/usr/bin/python3
# Working with the data

import spacy
import pandas as pd
import nltk
import sys # For command line inputs
import argparse # For better command line inputs.
from nltk.tokenize import WhitespaceTokenizer, sent_tokenize
from alive_progress import alive_bar # I like this progress bar better...
from tqdm import tqdm # ...but this progress bar works better for pandas operations

parser = argparse.ArgumentParser(prog='dataWork', description='Tidies up the data provided to it')
parser.add_argument('filename')
parser.add_argument('outfile')
parser.add_argument('-p', '--pandas', action='store_true')
args = parser.parse_args()

if args.pandas == True:
    tqdm.pandas() # Progress bar for pandas stuff.

    print("Reading data...")
    rdq = pd.read_csv(f"./csvs/{args.filename}.csv")
    print("Done.")
    if args.filename == 'discogs_data':
        rdq = rdq.query('data_quality != "Needs Major Changes"')
    rdq = rdq[rdq['profile'].notnull()] # Filter down the data to stuff we can actually use
    rdq['profile'] = rdq['profile'].str.replace(r"\n", " ") # Remove the \n from the profiles so they don't cause any issues.
    rdq['all_hyperlinks'] = rdq['profile'].str.extract(r'\[(.*?)\]') # Regex to just get anything within square brackets.
    # rdq[['hl_type', 'hyperlink_replace']] = rdq['all_hyperlinks'].str.extract(r'\[(\w+)(?:=([^\]]+))?\]') # Regex to get just names or numbers
    # rdq['hl_rep'] = rdq.apply(lambda row: (row['hl_type'], row['all_hyperlinks']), axis=1) # Combine to get a tuple of (artist/label, name)
    # print(rdq['hl_rep'].head(3))

    # Define regex patterns
    pattern_a_equals = r"\[\s*a\s*=\s*([^\]]+)\s*\]"
    pattern_a_number = r"\[\s*(a\d+)\s*\]"

    # Remove square brackets and 'a=' while keeping 'a' in the number format
    rdq["cleaned_sentence"] = rdq["profile"].str.replace(pattern_a_equals, r"\1", regex=True)
    rdq["cleaned_sentence"] = rdq["cleaned_sentence"].str.replace(pattern_a_number, r"\1", regex=True)

    rdq.to_csv(f'./csvs/{args.outfile}.csv') # Write dataframe to CSV.
    print(rdq['cleaned_sentence'][0])
    print("Cleaned dataframe now outputted to CSV.")

else:

    print("You forgot the -p at the end. Please use this for Pandas stuff.")