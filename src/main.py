
from input_output import read_lines_from_file, write_string_to_file, read_csv_to_data_frame, read_file_as_string
from metrics.LLM_query_complexity import LLM_query_complexity
import os
from evaluator import triplet_extraction
from metrics.LLM_cq_coverage import cq_coverage
from metrics.NLP_complexity import query_complexity
import re
from workflows.ontogenia import Ontogenia
from workflows.blank import Blank

def main_loop(model=None, workflow='Blank', parameters=[5,'gemini',-1]):
    cqs = read_lines_from_file('data/input_cqs/input_cqs.txt')

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


    triplet_extraction('data/ontologies/ontology.txt')
    print('cqs in main' + str(cqs))
    coverage = cq_coverage(cqs,'gemini')

    average_complexity = query_complexity(read_lines_from_file('data/addressed_cqs/addressed_cqs.txt'),read_csv_to_data_frame('data/extracted_triplets/ontology_triplets.csv'))
    LLM_complexity = LLM_query_complexity(read_lines_from_file('data/addressed_cqs/addressed_cqs.txt'), model, read_file_as_string('data/ontologies/ontology.txt'))


main_loop()

    


