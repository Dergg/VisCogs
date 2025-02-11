# Imports
import argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser(prog='similarity_scorer', description='Similarity score between 2 text files')
parser.add_argument('infile')

args = parser.parse_args()

# Scoring

# Function to read and parse the expected results from a text file
def parse_tts(file_path):
    expected = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    entry = {}
    for line in lines:
        line = line.strip()  # Remove extra spaces or newlines
        if line.startswith("Label:"):
            if entry:  # Save previous entry before starting a new one
                expected.append(entry)
            entry = {"Label": line.replace("Label: ", "").strip()}

        elif line.startswith("Founders:"):
            entry["Founders"] = line.replace("Founders: ", "").strip()

        elif line.startswith("Year:"):
            entry["Year"] = line.replace("Year: ", "").strip()

    if entry:  # Add the last entry
        expected.append(entry)

    print(f'Expected: {expected}')

    return expected

expected_results = parse_tts('./txts/expected_output.txt')
generated_results = parse_tts(f'./txts/{args.infile}.txt')

# String similarity function
def similarity_score(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Compute accuracy
def evaluate_results(expected, generated):
    total_score = 0
    max_score = 30  # Each entry has Label, Year, and Founders (3 fields)

    print(f'Expected: {expected}')
    print(f'Generated: {generated}')

    for exp, gen in zip(expected, generated):
        if exp['Label'] == 'Unknown':
            label_score = 1 if exp['Label'] == gen['Label'] else 0
        else:
            label_score = similarity_score(exp["Label"], gen["Label"])
        year_score = 1 if exp["Year"] == gen["Year"] else 0  # Exact match for year
        if exp['Founders'] == 'Unknown':
            founder_score = 1 if exp['Founders'] == gen['Founders'] else 0
        else:
            founder_score = similarity_score(exp["Founders"], gen["Founders"])

        entry_score = label_score + year_score + founder_score
        total_score += entry_score

        # Print individual entry comparison
        print(f"Expected: {exp}")
        print(f"Generated: {gen}")
        print(f"Scores -> Label: {label_score:.2f}, Year: {year_score}, Founders: {founder_score:.2f}\n")

    final_score = (total_score / max_score) * 100
    return final_score

# Compute similarity score
final_similarity = evaluate_results(expected_results, generated_results)

print(f"Overall Similarity Score: {final_similarity:.2f}%")