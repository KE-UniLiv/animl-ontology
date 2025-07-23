from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.generator import call_generator
from prompts import SQARQL_prompt

def LLM_query_complexity(addressed_cqs, model,ontology):
    return None
    #for entry in addressed_cqs:
    #    SQARQL_query = call_generator(SQARQL_prompt, entry, model)


