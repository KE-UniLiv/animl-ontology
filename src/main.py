
from input_output import read_lines_from_file, write_string_to_file, read_csv_to_data_frame, read_file_as_string
from metrics.LLM_query_complexity import LLM_query_complexity
from evaluator import triplet_extraction
import re
import sys
from metrics.LLM_cq_coverage import cq_coverage
from metrics.NLP_complexity import query_complexity
from workflows.ontogenia import Ontogenia
from workflows.blank import Blank
import rdflib
import os
from rdflib import Graph, RDF, BNode
from deeponto.onto.projection import OntologyProjector
from deeponto.onto import Ontology

def main_loop(ontology, workflow, parameters):
    cqs = read_lines_from_file(f'data/input_cqs/{ontology}.txt')

    #write_string_to_file(f'ontologies/ontology.txt', '')

    while parameters[len(parameters)-1] != 1:
        fragment,parameters = globals()[workflow](parameters,cqs,ontology)
        if fragment != None:
            print(fragment)
            pattern = r'(<\?xml version="1\.0"\?>.*?</rdf:RDF>)'
            match = re.search(pattern, fragment, re.DOTALL)
            print('life is a series loosely connected disappointments' + str(match))
            if match:
                print('it got though first round')
                try:
                    g = Graph()
                    g.parse(data=match.group(0), format="xml")  # or "turtle", "n3", etc
                    old_value = read_file_as_string(f'data/ontologies/{ontology}.txt')
                    try:
                        print('it got though second round')

                        write_string_to_file(f'data/ontologies/{ontology}.txt', match.group(1))
                        projector = OntologyProjector(bidirectional_taxonomy=False, only_taxonomy=True, include_literals=True)
                        onto = Ontology(f'data/ontologies/{ontology}.txt')
                        triplets = projector.project(onto)
                        print('it passed, and as such the ontology file should at least exist')
                    except:
                        print('anonymous objects')
                        parameters[3].pop()
                        parameters[len(parameters)-1] = 0
                        write_string_to_file(f'data/ontologies/{ontology}.txt',old_value)
                except:
                    print('invalid rdf syntax')
                    parameters[3].pop()
                    parameters[len(parameters)-1] = 0
            else:
                print('invalid start or close tag')
                parameters[3].pop()
                parameters[len(parameters)-1] = 0

       # except:
        #    parameters[3].pop()



    #triplet_extraction(f'data/ontologies/{ontology}.txt',ontology)

    #coverage = cq_coverage(cqs,parameters[1],ontology)

    #print('coverage: ' + str(coverage))

    #average_complexity = query_complexity(read_lines_from_file(f'data/addressed_cqs/{ontology}.txt'),read_csv_to_data_frame(f'data/extracted_triplets/{ontology}.csv'),ontology)

    #print('average centrality: ' + str(average_complexity))
    LLM_complexity = LLM_query_complexity(read_lines_from_file(f'data/addressed_cqs/{ontology}.txt'), parameters[1], read_file_as_string(f'data/ontologies/{ontology}.txt'))
    print('complexity:' +str(LLM_complexity))




if __name__ == "__main__":
    args = sys.argv[1:]  # Skip the script name
    print(args)
    arg1 = args[0]
    arg2 = args[1] if len(args) > 1 else 'Blank'
    arg3 = args[2] if len(args) > 2 else [5,'gemini',-1]
    main_loop(arg1, arg2, arg3)
 # Takes the first command-line argument


    


