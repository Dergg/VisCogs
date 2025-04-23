import json
import argparse

parser = argparse.ArgumentParser(prog='jsonify', description='Convert text file into JSON')
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

def parse_text_file(input_file, output_file):
    records = []
    record = {}


    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            print(f"Parsing line: {line}")
            line = line.strip()
            if not line or '::' not in line:
                if record:  
                    records.append(record)  
                    record = {}  
                continue

            key, value = line.split(":: ", 1)
            record[key] = value

    if record:
        records.append(record)

    with open(output_file, 'w+', encoding='utf-8') as json_file:
        json.dump(records, json_file, indent=4)
    
    print("File successfully outputted.")

try:
    parse_text_file(f"./txts/{args.infile}.txt", f"./jsons/{args.outfile}.json")
except FileNotFoundError:
    print(f'{args.infile}.txt not found in the ./txts folder. Please check your spelling and that the file exists.')