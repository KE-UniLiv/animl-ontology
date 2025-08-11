import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.input_output import read_file_as_string, write_string_to_file
from prompts import memorylessCQbyCQ, user_prompt
from src.generator import call_generator

def MemorylessCQbyCQ(parameters,cqs,ontology):
    print('Ontogenia workflow started--------------------------------------------------------------------')
   # print('starting with parameters:' + str(parameters))

    if parameters[len(parameters)-1] == -1:
        try:
            write_string_to_file(f'data/ontologies/{ontology}.ttl','')
        except:
            nothing = None
        batches = []
        parameters.insert(-1, cqs)
        parameters.insert(-1, [])
        parameters[len(parameters)-1] = 0
        return None,parameters
    
    elif parameters[len(parameters)-1] == 0:
        print(len(parameters[2]), len(parameters[3]))
        if len(parameters[2]) > len(parameters[3]):
            parameters[3].append(parameters[2][len(parameters[3])])
            fragment = call_generator(parameters[1],user_prompt+str(parameters[3]), (memorylessCQbyCQ))
            print('this is the fragment' + str(fragment))
            existing = read_file_as_string(f'data/ontologies/{ontology}.ttl')
            fragment = existing + str(fragment)
            return fragment, parameters
        
        else:
            parameters[len(parameters)-1] = 1
            return read_file_as_string(f'data/ontologies/{ontology}.ttl'),parameters