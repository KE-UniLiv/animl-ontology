import os
import pandas as pd
import csv

def read_lines_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.rstrip('\n') for line in file]
    return lines

def read_file_as_string(file_path):
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    else:
        return ''
    
def write_string_to_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_csv_to_data_frame(csv_file):
    try:
        df = pd.read_csv(csv_file, sep='\t')  # Read CSV file with tab delimiter
        return df
    except Exception as e:
        return
    
def save_to_csv(data):
    # Specify the desired file path and name
    file_path ='data/extracted_triplets/ontology_triplets.csv'
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t') # the s, p, o saves in the csv file and seperated by space no commas if i want comma delete the delimiter
        writer.writerows(data)