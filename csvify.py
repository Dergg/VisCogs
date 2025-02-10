# CSV-ify the test sentences into the same format as the discogs data.

# For NELM, we need it in the following format...
# id, name (label name), parent name, profile (already in text file)

import pandas as pd
import argparse

file_path = "test_sentences.txt" 
with open(file_path, "r") as file:
    lines = file.readlines()

lines = [line.strip() for line in lines if line.strip()]
df = pd.DataFrame(lines, columns=["profile"])

# Adding additional information to make it closer to what we expect to see in the Discogs dataset

id = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # IDs so we know the labels are different
name = ['Label Alpha', 'Bravo Records', 'Charlie and Co', 'Delta Force', 'Echoplex', 'Foxxtrott',
        'Grey Skies Records', 'Waving Records', 'Death Wish', 'JKR']
# We can skip parent name for now.
df['id'] = id
df['name'] = name

print(df)
df.to_csv('test_sentences.csv')
print("CSV made.")

