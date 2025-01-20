import spacy
import pandas as pd
import nltk
import sys # For command line inputs
from nltk.tokenize import WhitespaceTokenizer, sent_tokenize
from alive_progress import alive_bar # I like this progress bar better...
from tqdm import tqdm # ...but this progress bar works better for pandas operations

rdq = pd.read_csv("cleaned.csv")
tqdm.pandas() # For pandas magic (progress bars, yippee)

wtk = WhitespaceTokenizer()
print("Tokenising profiles...")
rdq['sentences'] = rdq['cleaned_sentence'].progress_apply(lambda x: sent_tokenize(x))
print(rdq['sentences'].values[0])
rdq['profile_tokenised'] = rdq['cleaned_sentence'].progress_apply(lambda x: nltk.word_tokenize(x))
print("Profiles tokenised.")

def process_text(text):
    sentences = sent_tokenize(text)
    tagged_sentences = [nltk.pos_tag(nltk.word_tokenize(sentence)) for sentence in sentences]
    return tagged_sentences

print("Tagging sentences...")

# Apply the function to the DataFrame
rdq['tagged_sentences'] = rdq['cleaned_sentence'].progress_apply(process_text)
print("Done.")

rdq['profile_string'] = rdq['cleaned_sentence'].apply(lambda x: ' '.join([item for item in x]))
nltk.download('wordnet')
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
