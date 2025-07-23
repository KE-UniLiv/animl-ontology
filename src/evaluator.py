from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import torch

from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector
from src.input_output import save_to_csv




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
    
def triplet_extraction(ontology):
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
    save_to_csv(data) 


