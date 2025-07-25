
import spacy
from collections import deque, defaultdict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.generator import call_generator
from prompts import retrofit_cq_prompt
from src.evaluator import  find_cosine_distances, greatest_similatirty
from src.input_output import read_csv_to_data_frame, save_array_to_file


def generate_questions_from_csv(triplets,model):

    df_chunks = [triplets[i:i+10] for i in range(0, triplets.shape[0], 5)]  # Split data into chunks for processing

    generated_cqs = []
    lines = []

    for i, chunk in enumerate(df_chunks):
        rows = chunk.values.tolist()
        for j,row in enumerate(rows):
        #complete_prompt = f"Subject: {row[0]}, Predicate: {row[1]}, Object: {row[2]}" # Create prompt from CSV row data
            complete_prompt = f"{', '.join(row)}?"  # Convert chunk to list format for question generation
        questions = call_generator(retrofit_cq_prompt,complete_prompt,model)  # Generate questions for each row in the chunk
        questions_list = [questions.strip().split('\n')]
        print(questions_list)
        generated_cqs.extend(questions_list)
    
    print('these are the cqs being dropped')
    return generated_cqs

def findBERTScore(generated_cqs,true_cqs):
    cosine_scores = find_cosine_distances(true_cqs,generated_cqs)
    BERTScore = greatest_similatirty(cosine_scores)

    return BERTScore


def cq_coverage(true_cqs,model,ontology):
    generated_cqs = generate_questions_from_csv(read_csv_to_data_frame(f'data/extracted_triplets/{ontology}.csv'),model)
    print(generated_cqs)
    greatest_similarity_cqs = findBERTScore(generated_cqs,true_cqs)
    addressed_cqs = [cq for cq, sim in zip(true_cqs, greatest_similarity_cqs) if sim < 0.5]

    save_array_to_file(addressed_cqs,f'data/addressed_cqs/{ontology}.txt')
    
    return len(addressed_cqs)/len(true_cqs)



