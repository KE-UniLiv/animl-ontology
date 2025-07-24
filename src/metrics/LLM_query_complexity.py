from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector
import sys
import os
from rdflib import Graph
import re
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.input_output import read_file_as_string, read_lines_from_file
from src.generator import call_generator
from prompts import SQARQL_prompt, benchmark_SPARQL

def LLM_query_complexity(addressed_cqs, model,ontology):
    for cq in addressed_cqs:
        print('this is the cq' + str(cq))
        context = f"""you are instructed to translate this competency question: {cq} into SPARQL
        this operation is about the following ontology: {ontology}, as stated in the primary prompt,
        
        do not attempt to create translations from nothing, and instead base your translations on the example
        translations provided here: {read_file_as_string('data/example_translations.txt')} the correct URL prefix is https://w3id.org/polifonia/ontology/music-meta/"""
        SQARQL_query = call_generator(context,benchmark_SPARQL, model)
        time.sleep(10)
        match = re.search(r'PREFIX.*?\}', SQARQL_query, re.DOTALL)
        if match:
            print(match)
            print('this is the stripped query' +str(match.group(0)))
            functionality = query_checker(ontology,match.group(0))
        else:
            if SQARQL_query != '':
                raise ValueError('LLM produced a regex invalid SPAQRQL query:' + SQARQL_query)

def query_checker(ontology,SPARQL_query):   
   # try:
        g = Graph()
        g.parse(data=ontology, format="xml") 
        results = g.query(SPARQL_query)
        print('these are the results:')
        print(results.askAnswer)
        for row in results:
            print(row)
   # except:
       # print('malformed sparql')

query_checker(read_file_as_string('data/ontologies/ontology.txt'),'''
PREFIX music-meta: <https://w3id.org/polifonia/ontology/music-meta/>

SELECT DISTINCT ?award WHERE {
    ?artist a music-meta:106ducks .
    ?artist music-meta:greg ?award .
}''')



#LLM_query_complexity(read_lines_from_file('data/addressed_cqs/addressed_cqs.txt'),'gemini',read_file_as_string('data/ontologies/ontology.txt'))
