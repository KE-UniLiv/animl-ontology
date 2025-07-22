
from input_output import read_lines_from_file, write_string_to_file
import os
from evaluator import cq_coverage
import re
from workflows.ontogenia import Ontogenia
from workflows.blank import Blank

def main_loop(model=None, workflow='Blank', parameters=[5,'gemini',-1]):
    cqs = read_lines_from_file('cqs.txt')

    #write_string_to_file(f'ontologies/ontology.txt', '')

    while parameters[len(parameters)-1] != 1:
        fragment,parameters = globals()[workflow](parameters,cqs)
        pattern = r'(<\?xml version="1\.0"\?>.*?</rdf:RDF>)'
        match = re.search(pattern, fragment, re.DOTALL)
        if match:
            print('Ontology fragment received, writing to file...')
            write_string_to_file(f'ontologies/ontology.txt', match.group(1))
        else:
            if fragment != '':
                raise ValueError('LLM produced an invalid ontology fragment:' + fragment)



    cq_coverage('ontologies/ontology.txt',cqs)


main_loop()

    


