import os

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