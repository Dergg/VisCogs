# Working with the data

import spacy
import nltk
import pandas as pd
from nltk.tokenize import RegexpTokenizer

recordData = pd.read_csv("discogs_data.csv")
rdq = recordData.query('data_quality != "Needs Major Changes"')
rdq = rdq[rdq['profile'].notnull()] # Filter down the data to stuff we can actually use
rdq['all_hyperlinks'] = rdq['profile'].str.extract(r'\[(.*?)\]') # Regex to just get anything within square brackets.

regexp = RegexpTokenizer('\w+')
rdq['profile_tokenized'] = rdq['profile'].apply(regexp.tokenize) # The mixing of Zs and Ss annoy me. >:/

