from src.input_output import read_file_as_string

def Blank(parameters,cqs,ontology):
    batches = []
    for i in range(0, len(cqs), parameters[0]):
        batches.append(str(cqs[i:i + parameters[0]]))
    parameters.insert(-1, batches)
    parameters.insert(-1, [])
    parameters[len(parameters)-1] = 1
    return read_file_as_string(f'data/ontologies/{ontology}.ttl'),parameters