from generator import call_gemini_api
from prompts import user_prompt, ontogenia
from input_output import read_lines_from_file, write_string_to_file
import os
from evaluator import eurecom_baseline

def main_loop(model=None, user_prompt=user_prompt, system_prompt=ontogenia, evaluation_metric=None,evaluation_mechanism=None,batch_size=5):
    cqs = read_lines_from_file('cqs.txt')
    batches = []
    for i in range(0, len(cqs), batch_size):
        batches.append(str(cqs[i:i + batch_size]))

    attached_batches = []

    for i in range(0,len(batches)):
        attached_batches.append(batches[i])
        fragment = call_gemini_api(user_prompt+str(attached_batches), system_prompt)
        write_string_to_file(f'ontologies/ontology.txt', fragment)
    
    print('yeet')

    eurecom_baseline()

main_loop()

    


