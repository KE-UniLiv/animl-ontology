from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import torch
from rdflib import Graph, RDF, BNode
from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector
import sys
import os
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.input_output import save_to_csv, overwrite_first_line, read_lines_from_file, write_string_to_file, save_array_to_file
from supporting_repositories.Auto_KGQA.API.create_indexes import createIndexes
from supporting_repositories.Auto_KGQA.API.core.QuestionHandler import run_question



np.random.seed(42)
torch.manual_seed(42)

def greatest_similatirty(similarities):
    greatest_similarity = []

    for row in similarities:
        greatest_similarity.append(float(np.min(row)))

    return greatest_similarity


def most_similar_object(similarities):
    greatest_similarity = []

    for row in similarities:
        greatest_similarity.append(float(np.argmin(row)))

    return greatest_similarity

def find_cosine_distances(objects, objects_to_be_compared_with):
    model = SentenceTransformer('all-mpnet-base-v2')
    vectors = model.encode(objects, convert_to_tensor=True)
    vectors_to_be_compared_with = model.encode(objects_to_be_compared_with, convert_to_tensor=True)

    if len(vectors.shape) == 1:
        vectors = vectors.reshape(1, -1)

    similarities = cosine_distances(vectors, vectors_to_be_compared_with)

    return similarities

def nearest_neighbors(generated_resources, true_resources):

    return most_similar_object(find_cosine_distances(generated_resources, true_resources))
    
def triplet_extraction(ontology,file_name):
    onto = Ontology(ontology)
    projector = OntologyProjector(bidirectional_taxonomy=False, only_taxonomy=True, include_literals=True)

    # Project the ontology into triples
    projected_ontology = projector.project(onto)

    #--- A function that only returns the concepts of s, p, o
    def con(c):
        return c.rsplit('#')[-1]



    for subj, pred, obj in projected_ontology:
        # Check if there is at least one triple in the Graph
        if (subj, pred, obj) not in projected_ontology:
            raise Exception("It better be!")

    #--- Print the number of "triples" in the Graph

    # extract s, p, o and save it to the list to be saved in csv file
    data= []
    for s,p,o in projected_ontology:
        sub = con(s)  
        pre = con(p) 
        obj = con(o)  
        data.append([sub, pre, obj])
    save_to_csv(data,f'data/extracted_triplets/{file_name}.csv') 

def evaluator(ontology):
    overwrite_first_line("supporting_repositories/Auto_KGQA/API/configs.py",f'ENDPOINT_KNOWLEDGE_GRAPH_URL = "c:/Users/sgwmorli/internship_stage_2/animl_ontology/animl-ontology/data/ontologies/{ontology}.ttl"')
    createIndexes()
    cqs = read_lines_from_file(f'data/input_cqs/{ontology}.txt')
    average = 0
    library = []
    for cq in cqs:
        result = run_question(cq)
        write_string_to_file(f'supporting_repositories/OWLUnit/tests/{(cq[:-1].replace(' ','_')).replace('/','_')}.ttl',f'''
        @prefix owlunit: <https://w3id.org/OWLunit/ontology/> .
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix owlunittest: <https://w3id.org/OWLunit/test/> .

        owlunittest:primary  a owlunit:CompetencyQuestionVerification ;
 	        owlunit:hasCompetencyQuestion "{cq}" ;
 	        owlunit:hasSPARQLUnitTest """
	            {result['sparql']}""" ;
	        owlunit:testsOntology <../../../data/ontologies/ontology.ttl> .''')
        
        print("Current working directory:", os.getcwd())
        output = subprocess.run(["java", "-jar", 'supporting_repositories/OWLUnit/OWLUnit-0.3.2.jar', "--test-case", "https://w3id.org/OWLunit/test/primary","--filepath",f"supporting_repositories/OWLUnit/tests/{(cq[:-1].replace(' ','_')).replace('/','_')}.ttl"], capture_output = True)
        print(output)
        if str(output).__contains__('PASSED'):
            average += 1
            result['correctness'] = True
        else:
            result['correctness'] = False
        print(result['correctness'])
        library.append(result)
    average = average/len(cqs)
    print(average)
    save_array_to_file(library,f'data/addressed_cqs/{ontology}.txt')



