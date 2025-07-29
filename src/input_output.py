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
    try:
        f = open(file_path, "x")
    except:
        Nothing = None
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_csv_to_data_frame(csv_file):
    try:
        df = pd.read_csv(csv_file, sep='\t')  # Read CSV file with tab delimiter
        return df
    except Exception as e:
        return
    
def save_array_to_file(array, filename):
    try:
        f = open(filename, "x")
    except:
        Nothing = None
    with open(filename, 'w') as f:
        for item in array:
            f.write(f"{item}\n")

    
def save_to_csv(data,file_path):
    # Specify the desired file path and name
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t') # the s, p, o saves in the csv file and seperated by space no commas if i want comma delete the delimiter
        writer.writerows(data)

def overwrite_first_line(file_path,first_line):
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Replace the first line
    if lines:
        lines[0] = f'{first_line}\n'
    else:
        lines = [first_line]
# Write the modified lines back to the file
    with open(file_path, "w") as file:
        file.writelines(lines)