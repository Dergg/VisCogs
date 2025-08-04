# Deprecated. Do not use.

import spacy
import pandas as pd
import sys # For command line inputs
import argparse # For better command line inputs
from nltk.tokenize import WhitespaceTokenizer, sent_tokenize
from alive_progress import alive_bar # I like this progress bar better...
from tqdm import tqdm # ...but this progress bar works better for pandas operations
import traceback

parser = argparse.ArgumentParser(prog='tagger', description='Tags using NLTK or spaCy for further processing later')
parser.add_argument('filename') # Either the Discogs database or the hand-crafted dataset
parser.add_argument('option') # Replace build or test mode
parser.add_argument('outfile')
parser.add_argument('-nltk', '--use_nltk', action='store_true')
parser.add_argument('-spacy', '--use_spacy', action='store_true')

args = parser.parse_args()

rdq = pd.read_csv(f"./csvs/{args.filename}.csv")
tqdm.pandas() # For pandas magic (progress bars, yippee)

if args.use_nltk == True:
    import nltk
    from nltk.tokenize import WhitespaceTokenizer
#     wtk = WhitespaceTokenizer()
#     print("Tokenising profiles...")
#     rdq['sentences'] = rdq['cleaned_sentence'].progress_apply(lambda x: sent_tokenize(x))
#     print(rdq['sentences'].values[0])
#     rdq['profile_tokenised'] = rdq['cleaned_sentence'].progress_apply(lambda x: nltk.word_tokenize(x))
#     print("Profiles tokenised.")

if args.use_spacy == True:
    import spacy
    nlp = spacy.load('en_core_web_sm')

def process_text(text):
    if args.use_nltk == True:
        sentences = sent_tokenize(text)
        tagged_sentences = [nltk.pos_tag(nltk.word_tokenize(sentence)) for sentence in sentences]
        return tagged_sentences
    elif args.use_spacy == True:
        doc = nlp(text)
        sents = [sent.text for sent in doc.sents]
        print(f'Sentence: {sents[0]}')
        tagged_sentences = [[(token.text, token.pos_) for token in nlp(sentence)] for sentence in sents]
        print(f'Tagged sentence: {tagged_sentences[0]}')
        exp_tagged = nlp(sents[0])
        print(f'Tagged experimental: {exp_tagged}')
        return tagged_sentences

def tag_and_token(text):
    return text

print("Tagging sentences...")

# Apply the function to the DataFrame
rdq['tagged_sentences'] = rdq['cleaned_sentence'].progress_apply(process_text)
print("Done.")

rdq['profile_string'] = rdq['cleaned_sentence'].apply(lambda x: ' '.join([item for item in x]))
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger_eng')
# nltk.download('punkt_tab')
# ^^ Above packages have already been downloaded.

print(rdq.iloc[0]['tagged_sentences'])
print("Tagging tokens...")
try:
    if args.option == 'test':
        rdq['tagged_tokens'] = rdq['tagged_sentences'].head(1000).progress_apply(lambda x: tag_and_token(x)) # tag_and_token does nothing.
    elif args.option == 'build':
        print("Build mode has been specified. Please be patient, this might take a little while.")
        rdq.to_csv(f'./csvs/{args.outfile}.csv') # Write dataframe to CSV.
        print("Dataframe written to CSV file.")
    else:
        print("You have not specified a tagging method. Please use test or build depending on what you want.")
except Exception as e:
    traceback.print_exc()
    print("No command specified. Please use 'test' or 'build' when running the program to correctly tag tokens.")
    exit()
print("Done.")
print(rdq.iloc[2]['tagged_sentences']) # Show the head for now. We can build from this later.
