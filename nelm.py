#!/usr/bin/python3
# Node & Edge List Maker Program
# Take things from the processed and tagged Discogs data.

import sys
import argparse
from ast import literal_eval
import traceback
import re
from collections import defaultdict
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

parser = argparse.ArgumentParser(prog='nelm', description='Generate node and edge list')
parser.add_argument('infile') # Specify the file going in
parser.add_argument('-n', '--node', action='store_true')
parser.add_argument('-e', '--edge', action='store_true')
parser.add_argument('-x', '--experiment', action='store_true')
args = parser.parse_args()

tqdm.pandas()

print("Reading data...")
data = pd.read_csv(f'{args.infile}.csv')
print("Complete.")

def find_fullstop(sentence):
    for i in range(len(sentence)):
        if sentence[i][0] == '.':
            print(f'Found fullstop at index {i}')
            return i

try:
    if args.node == True:
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

    elif args.edge == True:
        print("WIP")
    elif args.experiment == True:
        print("Please be aware that experimentation can cause severe brain messery.")
        target_words = ["founded", "formed"]
        surrounding_context = []
        scfull = False
        for idx, tagged_sentence in enumerate(data['tagged_sentences']):
            ts = literal_eval(tagged_sentence) # Convert into list as it is a string for some reason
            if scfull == True:
                break
            for i, (word, tag) in enumerate(ts[0]):
                if scfull == True:
                    break
                if word.lower() in target_words and scfull == False:
                    context = ts[0]
                    name = data.iloc[idx]['name']
                    print(f'Found word: {word}\n Context: {context}')
                    surrounding_context.append((context, name)) # Surrounding context is a list of tuples in the form (list, string)
                    # Each "context" itself is also a list of tuples.
                    # if len(surrounding_context) >= 10:
                    #     scfull = True
                    #     break
        
        print(f'Found {len(surrounding_context)} different sentences.') 

        # Pattern matching goes here, make sure you account for format (word, tag)
        
        # NLTK Patterns
        patterns = [
            re.compile(r'VBN IN CD IN (NNP|NN)+'),
            re.compile(r'VBN IN CD'),
            re.compile(r'VBN IN (NNP|NN)+')
        ] # Add more to this later if things aren't getting caught
        # See if spaCy can get these patterns too? Penn Treebank Project POS tags




        # Extracted information
        extracted_info = []

        print("Surrounding context:", surrounding_context)
        for context, label_name in surrounding_context:
            print(f'Context: {context}')
            print(f'Label name: {label_name}')
            words, tags = zip(*context)  # Separate words and tags
            print(f'Words: {words}')
            print(f'Tags: {tags}')
            sentence = ' '.join(words) # For experimentation purposes
            pos_sequence = ' '.join(tags)  # Join POS tags as a single string

            print(f'Sentence: {sentence}')
            print(f'Sequence: {pos_sequence}')
            
            # Check for patterns in the POS sequence
            for pattern in patterns:
                match = pattern.search(pos_sequence)
                if match:
                    year_idx = -1 # Placeholder value
                    noYear = False # If no year is in the 'founded' area
                    print(f'Matched! Pattern is {pos_sequence[match.start():match.end()]}')
                    print(f'Match starts at character {match.start()} and ends at character {match.end()}')
                    print(tags[match.start():match.end()])
                    if 'CD' in pos_sequence[match.start():match.end()]:
                        # Extract year (first occurrence of CD in matched part)
                        year_idx = tags.index('CD')
                        print(f'Year index = {year_idx}')
                        year = words[year_idx]
                        print(f'Year extracted: {year}')
                    else:
                        year = 'Unknown'
                        print("Year not successfully extracted. Marking as 'unknown'.")
                    
                    # Extract founders (words after 'by' or similar patterns)
                    if 'IN' in tags[year_idx + 1:] and (year_idx != -1 or noYear == True):  # Check for "by" after the year
                        by_idx = tags.index('IN', year_idx + 1)  # Index of "by"
                        potential_founders = words[by_idx + 1:]  # Words after "by"
                        
                        founders = []
                        
                        for word, tag in zip(potential_founders, tags[by_idx + 1:]):
                            if tag == "NNP":  # Only consider proper nouns
                                founders.append(word)
                        
                        founders = ' '.join(founders) if founders else "Unknown"
                        if label_name in founders:
                            founders.replace(label_name, "")
                    else:
                        founders = "Unknown"
                    
                    extracted_info.append({
                        'label': label_name,
                        'year': year,
                        'founders': founders
                    })

                    if year == 'Unknown' and founders == 'Unknown':
                        print(sentence)

                    break

        # Print extracted information
        for info in extracted_info:
            print(f"Label: {info['label']}\nYear: {info['year']}\nFounders: {info['founders']}\n")

        # NOTE: The year seems to be extracting successfully, the biggest issue now is trying to figure out the Founders thing.
        # print(f'Surrounding context type = {type(surrounding_context)}')
        # breakdown = surrounding_context
        # print(type(breakdown))

        #########################
        ### SCORING GOES HERE ###
        #########################

        # Function to write generated results to a text file
        def write_results_to_file(results, file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                for entry in results:
                    file.write(f"Label: {entry['label']}\n")
                    file.write(f"Year: {entry['year']}\n")
                    file.write(f"Founders: {entry['founders']}\n\n")  # Add spacing

        write_results_to_file(extracted_info, 'nltkgenout.txt')


    elif sys.argv[1] == 'test':
        print("Test")
    else:
        print("Please specify if you want to make an edge or a node list.")

except Exception:
    traceback.print_exc() # Prints  the full exception / error
    print("Please specify if you want to make a node or edge list using 'node' or 'edge' after calling program.")
    exit()