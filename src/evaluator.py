from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import torch
# from deeponto.onto import Ontology
# from deeponto.onto.projection import OntologyProjector
import sys
import os
import threading
import queue
import statistics
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.input_output import save_to_csv
from metrics.autoUnit import autoUnit
from src.input_output import save_to_csv, overwrite_first_line, read_lines_from_file, write_string_to_file, save_array_to_file
from supporting_repositories.Auto_KGQA.API.create_indexes import createIndexes




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


    # extract s, p, o and save it to the list to be saved in csv file
    data= []
    for s,p,o in projected_ontology:
        sub = con(s)  
        pre = con(p) 
        obj = con(o)  
        data.append([sub, pre, obj])
    save_to_csv(data,f'data/extracted_triplets/{file_name}.csv') 

stop_event = threading.Event()



def error_maker():
    time.sleep(40)
    stop_event.set()
    raise ValueError('derliberate error')

def evaluation_runner(metrics):
    for metric in metrics:
        output_queue = queue.Queue()
        metric['parameters']['initialisation_step'] = 1
        target=globals()[metric['name']](metric['parameters'],0,output_queue,stop_event)
        metric['parameters']['initialisation_step'] = 0
        parameters = output_queue.get()
        if not(parameters['paralleism_blocker'] == True):
            
            threads = []
            for i in range(1, 5):
                thread = threading.Thread(target=globals()[metric['name']], args=(parameters, i, output_queue,stop_event))
                thread.start()
                threads.append(thread)
        else:
            thread=globals()[metric['name']](metric['parameters'],0,output_queue,stop_event)
            thread.start()
            threads.append(thread)
        result = []

        for thread in threads:
            thread.join()
            while not output_queue.empty():
                result.append(output_queue.get())
        mean = statistics.mean(result)
        print('mean:' +str(mean))
        standard_deviation = statistics.stdev(result)
        print('standard deviation:' + str(standard_deviation))







