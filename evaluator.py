from input_output import read_file_as_string
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import torch
import csv
from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector
import pandas as pd
from generator import call_gemini_api
from prompts import retrofit_cq_prompt
from input_output import read_lines_from_file
import ast
import os


np.random.seed(42)
torch.manual_seed(42)



def BERTScoe(generated_resources, true_resources):
    
    model = SentenceTransformer('all-mpnet-base-v2')
    generated_embeddings = model.encode(generated_resources, convert_to_tensor=True)
    true_embeddings = model.encode(true_resources, convert_to_tensor=True)

    similarities = cosine_distances(generated_embeddings, true_embeddings)

    greatest_similarity = []

    for row in similarities:
        greatest_similarity.append(float(np.min(row)))

    return greatest_similarity
    
def BERTScore_distribution(similarities):
    total = len(similarities)
    if total == 0:
        return [0.0, 0.0, 0.0, 0.0]
    identical = sum(1 for x in similarities if x == 0)
    likely_synonym = sum(1 for x in similarities if 0 < x < 0.3)
    likely_related_concept = sum(1 for x in similarities if 0.3 <= x < 0.7)
    unrelated = sum(1 for x in similarities if x >= 0.7)
    return [
        identical / total * 100,
        likely_synonym / total * 100,
        likely_related_concept / total * 100,
        unrelated / total * 100
        ]


def principled_reuse(ontology,odp_set):
    class_regex = r'<(?:owl:Class|rdf:Description|rdfs:subClassOf)[^>]*?(?:rdf:about|rdf:resource)="[^"#]+[#/]([^"#/>]+)"'
    property_regex = r'<(?:rdf:Description|owl:ObjectProperty)[^>]*rdf:about="[^"#]+[#/]([^"#/>]+)"'

    primary_triplets = triplet_extraction(ontology)

    for filename in os.listdir(odp_set):
        file_path = os.path.join(odp_set, filename)
        if os.path.isfile(file_path):
            print(f"Processing file: {file_path}")
            # You can call resource_name_extractor or other logic here as needed


    greatest_similarity_classes = BERTScoe(generated_classes, true_classes)
    similarity_dist_classes = BERTScore_distribution(greatest_similarity_classes)

    print('distribution of class names similarity:')
    print(f'Identical: {similarity_dist_classes[0]:.2f}%') 
    print(f'Likely Synonym: {similarity_dist_classes[1]:.2f}%')
    print(f'Likely Related Concept: {similarity_dist_classes[2]:.2f}%')
    print(f'Unrelated: {similarity_dist_classes[3]:.2f}%')


    greatest_similarity_properties = BERTScoe(generated_properties, true_properties)
    similarity_dist_properties = BERTScore_distribution(greatest_similarity_properties)

    print('distribution of property names similarity:')
    print(f'Identical: {similarity_dist_properties[0]:.2f}%') 
    print(f'Likely Synonym: {similarity_dist_properties[1]:.2f}%')
    print(f'Likely Related Concept: {similarity_dist_properties[2]:.2f}%')
    print(f'Unrelated: {similarity_dist_properties[3]:.2f}%')


def triplet_extraction(ontology):
    onto = Ontology(ontology)
    projector = OntologyProjector(bidirectional_taxonomy=False, only_taxonomy=True, include_literals=True)

    # Project the ontology into triples
    projected_ontology = projector.project(onto)

    #--- A function that only returns the concepts of s, p, o
    def con(c):
        return c.rsplit('#')[-1]

    def save_to_csv(data):
        # Specify the desired file path and name
        file_path ='vicinity.csv'
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter='\t') # the s, p, o saves in the csv file and seperated by space no commas if i want comma delete the delimiter
            writer.writerows(data)


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


def generate_cqs(ontology):
    triplet_extraction(ontology)
    cqs = generate_questions_from_csv('ontology_triplets.csv')
    return cqs

# Function to read CSV file, generate questions, and save to Excel file
def generate_questions_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, sep='\t')  # Read CSV file with tab delimiter
    except Exception as e:
        return

    df_chunks = [df[i:i+10] for i in range(0, df.shape[0], 5)]  # Split data into chunks for processing

    generated_cqs = []

    for i, chunk in enumerate(df_chunks):
        rows = chunk.values.tolist()
        for row in rows:
        #complete_prompt = f"Subject: {row[0]}, Predicate: {row[1]}, Object: {row[2]}" # Create prompt from CSV row data
            complete_prompt = f"{', '.join(row)}?"  # Convert chunk to list format for question generation
        questions = call_gemini_api(retrofit_cq_prompt,complete_prompt)  # Generate questions for each row in the chunk
        questions_list = questions.strip().split('\n')
        generated_cqs.extend(questions_list)
        
    return generated_cqs 

def cq_coverage(ontology, true_cqs):
    generated_cqs = generate_cqs(ontology)
    greatest_similarity_cqs = BERTScoe(true_cqs, generated_cqs)
    similarity_dist_classes = BERTScore_distribution(greatest_similarity_cqs)

    print('distribution of precision bertScores for generated versuses true cqs:')
    print(f'definetly addressed: {similarity_dist_classes[0]:.2f}%') 
    print(f'Likely addressed: {similarity_dist_classes[1]:.2f}%')
    print(f'likely unaddressed: {similarity_dist_classes[3]+similarity_dist_classes[2]:.2f}%')
    

generate_questions_from_csv('vicinity.csv')  # Call function to generate questions from CSV file