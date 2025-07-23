from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.input_output import read_file_as_string
from src.generator import call_generator
from prompts import SQARQL_prompt

def LLM_query_complexity(addressed_cqs, model,ontology):
    for cq in addressed_cqs:
        context = f"""you are instructed to translate this competency question: {cq} into SPARQL
        this operation is about the following ontology: {ontology}, as stated in the primary prompt,
        
        do not attempt to create translations from nothing, and instead base your translations on the example
        translations provided here: {read_file_as_string('data/example_translations.txt')}"""
        SQARQL_query = call_generator(context,SQARQL_prompt, model)

        


