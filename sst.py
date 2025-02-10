# The Special SpaCy Tagger
# This uses a different tagging methodology to pick up on things a little better

import spacy
import pandas
import sys
import argparse
import traceback
import pandas as pd
from difflib import SequenceMatcher

parser = argparse.ArgumentParser(prog='sst', description='Special SpaCy Tagging software')
parser.add_argument('infile')
parser.add_argument('-sm', '--use_sm', action='store_true')
parser.add_argument('-lg', '--use_lg', action='store_true')
args = parser.parse_args()

if args.use_sm: # Simpler 
    nlp = spacy.load('en_core_web_sm') 

if args.use_lg: # More in-depth parsing
    nlp = spacy.load('en_core_web_lg')

df = pd.read_csv(f'{args.infile}.csv')

def extract_info(text):
    doc = nlp(text)

    label = 'Unknown'
    founders = []
    year = 'Unknown'

    print(doc)

    # Step 1: Use NER to extract known entities
    for ent in doc.ents:
        if ent.label_ == "ORG":  # Likely record labels
            label = ent.text
        elif ent.label_ == "PERSON":  # Founders
            founders.append(ent.text)
        elif ent.label_ == "DATE" and any(char.isdigit() for char in ent.text):  # Extract year
            year = ent.text

    # Step 2: Use Dependency Parsing to find subjects of "founded"
    for token in doc:
        if token.lemma_ == "found" and token.dep_ in {"ROOT", "acl"}:
            # Get subject (who founded the label)
            subj = [child for child in token.lefts if child.dep_ in {"nsubj", "nsubjpass"}]
            if subj:
                band_name = " ".join([t.text for t in subj[0].subtree])
                founders.append(band_name)

    founder = ""
    if len(founders) == 1:
        founder == founders[0]
        return {"Label": label, "Founders": founder, "Year": year}
    else:
        return {"Label": label, "Founders": list(set(founders)), "Year": year}


generated_results = []
# Extract information
for sentence in df['cleaned_sentence']:
    generated_results.append(extract_info(sentence))

# Function to write generated results to a text file
def write_results_to_file(results, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for entry in results:
            file.write(f"Label: {entry['Label']}\n")
            file.write(f"Year: {entry['Year']}\n")
            file.write(f"Founders: {entry['Founders']}\n\n")  # Add spacing

write_results_to_file(generated_results, 'genout.txt')
