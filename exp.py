

import spacy
import pandas as pd
import argparse
import re
import spacy.displacy as sd

# Argument parsing
parser = argparse.ArgumentParser(prog='sst', description='Special SpaCy Tagging software')
parser.add_argument('infile')
parser.add_argument('-sm', '--use_sm', action='store_true')
parser.add_argument('-lg', '--use_lg', action='store_true')
parser.add_argument('-displacy', '--displacy', action='store_true')
args = parser.parse_args()

# Load spaCy models
if args.use_sm:
    nlp = spacy.load('en_core_web_sm')
elif args.use_lg:
    nlp = spacy.load('en_core_web_lg')
else:
    print("No model specified, defaulting to en_core_web_sm.")
    nlp = spacy.load('en_core_web_sm')

# Read CSV file
try:
    df = pd.read_csv(f'./csvs/{args.infile}.csv')
except FileNotFoundError:
    print(f"Error: {args.infile}.csv not found in the ./csvs folder.")
    exit(1)

acq_vb = {'acquire', 'purchase', 'buy', 'merge', 'acquired', 'purchased', 'bought', 'merged'}

def extract_info(text):
    """Extracts Named Entities and Other Relevant Information from Text."""
    doc = nlp(text)
    label = "Unknown"
    founders = set()
    year = "Unknown"
    subject = 'Unknown'
    object_ = 'Unknown'
    event_type = 'FND' # Default to founding event
    
    # Extract earliest found year 
    years = [int(match.group()) for match in re.finditer(r'\b(19\d{2}|20\d{2})\b', text)]
    if years:
        year = str(min(years))

    # Extract entities (NER)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            founders.add(ent.text)
        elif ent.label_ == "ORG" and label == "Unknown":
            label = ent.text

    # If we're missing an organisation... use dependency parsing
    if label == "Unknown":
        for token in doc:
            if token.lemma_ in {"found", "create", "establish"}:
                candidates = [child.text for child in token.children if child.dep_ in {"nsubj", "dobj"}]
                if candidates:
                    label = max(candidates, key=len)

    # Extract numeric entity IDs (e.g., [a228172] → 228172)
    numeric_entities = re.findall(r'\[(?:[a-zA-Z])?(\d+)\]', text)
    if numeric_entities:
        founders.update(numeric_entities)

    # Extract additional founders with POS tagging (Proper Nouns)
    temp_name = []
    for token in doc:
        # Acquisition
        if token.lemma_.lower() in acq_vb:
            event_type = 'ACQ'
            for child in token.children:
                if child.dep_ in {'nsubj', 'nsubjpass'} and child.ent_type_ == 'ORG':
                    subject = child.text
            for child in token.children:
                if child.dep_ in {'dobj', 'pobj'} and child.ent_type_ == 'ORG':
                    object = child.text
            if subject == 'Unknown':
                for ent in doc.ents:
                    if ent.label_ == 'ORG':
                        subject = ent.text
                        break
            if object_ == 'Unknown':
                orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
                if len(orgs) > 1:
                    object_ = orgs[1]

            break

        # Founding events
        if token.pos_ == "PROPN":
            temp_name.append(token.text)
        elif temp_name:
            founders.add(" ".join(temp_name))
            temp_name = []

    # Return processed data
    if event_type == 'FND':
        return {
            "Type": event_type,
            "Label": label,
            "Founders": ", ".join(sorted(founders)) if founders else "Unknown",
            "Year": year
        }
    else: # ACQ
        return {
            "Type": event_type,
            "Subject": subject,
            "Object": object_,
            "Year": year
        }

# Process sentences
generated_results = [extract_info(sentence) for sentence in df['cleaned_sentence']]

# Write results to file
def write_results_to_file(results, file_path):
    """Writes extracted results to a text file in a structured format."""
    with open(file_path, "w", encoding="utf-8") as file:
        for res in results:
            if res['Type'] == 'FND':
                file.write(f'Type:: {res['Type']}\nLabel:: {res['Label']}\nYear:: {res['Year']}\nFounders:: {res['Founders']}\n\n')
            elif res['Type'] == 'ACQ':
                file.write(f'Type:: {res['Type']}\nSubject:: {res['Subject']}\nObject:: {res['Object']}\nYear:: {res['Year']}\n\n')

write_results_to_file(generated_results, './txts/genout.txt')

# Serve displacy visualizations (if requested)
if args.displacy:
    for sentence in df['cleaned_sentence']:
        nlps = nlp(sentence)
        sd.serve(nlps)
