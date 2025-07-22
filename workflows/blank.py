from input_output import read_file_as_string

def Blank(parameters,cqs):
    parameters[len(parameters)-1] = 1
    return read_file_as_string('ontologies/ontology.txt'),parameters