from src.input_output import read_file_as_string

def Blank(parameters,cqs,ontology):
    parameters[len(parameters)-1] = 1
    return read_file_as_string(f'ontologies/{ontology}.txt'),parameters