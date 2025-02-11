# The Special SpaCy Tagger
# This uses a different tagging methodology to pick up on things a little better

import spacy
import pandas
import sys
import argparse
import traceback
import pandas as pd
from difflib import SequenceMatcher
import re
from collections import Counter
from itertools import tee


parser = argparse.ArgumentParser(prog='sst', description='Special SpaCy Tagging software')
parser.add_argument('infile')
parser.add_argument('-sm', '--use_sm', action='store_true')
parser.add_argument('-lg', '--use_lg', action='store_true')
args = parser.parse_args()

if args.use_sm: # Simpler 
    nlp = spacy.load('en_core_web_sm') 

if args.use_lg: # More in-depth parsing
    nlp = spacy.load('en_core_web_lg')

try:
    df = pd.read_csv(f'./csvs/{args.infile}.csv')
except Exception as e:
    print(f'{args.infile}.csv not found in the ./csvs folder. Please check your spelling, or whether the file exists.')


def extract_info(text):
    doc = nlp(text)
    label = "Unknown"
    founders = []
    year = "Unknown"

    # Merge Entities to Keep Full Names Together
    with doc.retokenize() as retokenizer:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                retokenizer.merge(ent)

    # Extract Founders (NER + POS)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            founders.append(ent.text)

    # If no founders found via NER, use PROPN sequences
    if not founders:
        temp_name = []
        for token in doc:
            if token.pos_ == "PROPN": # This might not be brilliant, could pick up on people / place names?
                temp_name.append(token.text)
            elif temp_name:
                founders.append(" ".join(temp_name))
                temp_name = []

    # Extract label (generalized)
    label = next((ent.text for ent in doc.ents if ent.label_ == "ORG"), "Unknown")

    if label == "Unknown":
        for token in doc:
            if token.lemma_ in {"found", "create", "establish"}:
                candidates = [child.text for child in token.children if child.dep_ in {"nsubj", "dobj"}]
                if candidates:
                    label = max(candidates, key=len)  # Pick longest candidate

    # Extract year (choose the earliest year, naively)
    years = [int(match.group()) for match in re.finditer(r'\b(19\d{2}|20\d{2})\b', text)]
    if years:
        year = str(min(years))

    # Extract Founders Using Dependency Parsing (Without Over-Traversing)
    for token in doc:
        if token.lemma_ == "found" and token.dep_ in {"ROOT", "acl"}:
            for child in token.children:
                if child.dep_ in {"nsubj", "nsubjpass"}:
                    founders.append(child.text)  # Don't grab full subtree

    # Remove Duplicates & Cleanup
    founders = list(set(founders)) or "Unknown"

    return {"Label": label, "Founders": ", ".join(founders), "Year": year}

# Process all sentences
generated_results = [extract_info(sentence) for sentence in df['cleaned_sentence']]


generated_results = []
# Extract information
for sentence in df['cleaned_sentence']:
    generated_results.append(extract_info(sentence))
    
for i in range(len(generated_results)):
    print(generated_results[i])

# Function to write generated results to a text file
def write_results_to_file(results, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for entry in results:
            file.write(f"Label: {entry['Label']}\n")
            file.write(f"Year: {entry['Year']}\n")
            file.write(f"Founders: {entry['Founders']}\n\n")  # Add spacing

write_results_to_file(generated_results, './txts/genout.txt')
