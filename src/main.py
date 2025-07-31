
from input_output import read_lines_from_file, write_string_to_file
import sys
from workflows.ontogenia import Ontogenia
from workflows.blank import Blank
from metrics.autoUnit import autoUnit
from evaluator import evaluation_runner
from rdflib import Graph
import re


def main_loop(ontology, workflow, parameters):
    cqs = read_lines_from_file(f'data/input_cqs/{ontology}.txt')

    while parameters[len(parameters)-1] != 1:
        fragment,parameters = globals()[workflow](parameters,cqs,ontology)
        if fragment != None:
            try:
                fragment = re.search(r'@prefix.*\.', fragment, flags=re.DOTALL).group()
                g = Graph()
                g.parse(data=fragment, format="n3")
                write_string_to_file(f'data/ontologies/{ontology}.ttl',fragment)
                print('fragment parsed successfully')
            except:
                print('invalid rdf syntax')
                parameters[3].pop()
                parameters[len(parameters)-1] = 0
    
    evaluation_runner([{'name':'autoUnit','parameters':{'ontology':ontology}}])






if __name__ == "__main__":
    args = sys.argv[1:]  # Skip the script name
    print(args)
    arg1 = args[0]
    arg2 = args[1] if len(args) > 1 else 'Blank'
    arg3 = args[2] if len(args) > 2 else [5,'gemini',-1]
    main_loop(arg1, arg2, arg3)
 # Takes the first command-line argument


    


