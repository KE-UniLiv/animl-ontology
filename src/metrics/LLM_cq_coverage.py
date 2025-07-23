
import spacy
from collections import deque, defaultdict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.generator import call_generator
from prompts import retrofit_cq_prompt
from src.evaluator import nearest_neighbors, find_cosine_distances, greatest_similatirty, most_similar_object
from src.input_output import write_string_to_file, read_csv_to_data_frame


def generate_questions_from_csv(triplets,model):

    df_chunks = [triplets[i:i+10] for i in range(0, triplets.shape[0], 5)]  # Split data into chunks for processing

    generated_cqs = []
    lines = []

    for i, chunk in enumerate(df_chunks):
        print(chunk)
        print(i)
        rows = chunk.values.tolist()
        for j,row in enumerate(rows):
        #complete_prompt = f"Subject: {row[0]}, Predicate: {row[1]}, Object: {row[2]}" # Create prompt from CSV row data
            complete_prompt = f"{', '.join(row)}?"  # Convert chunk to list format for question generation
        questions = call_generator(retrofit_cq_prompt,complete_prompt,model)  # Generate questions for each row in the chunk
        questions_list = [questions.strip().split('\n')]
        for counter in range(len(questions_list)):
            lines.append(((5*i)+j))
        generated_cqs.extend(questions_list)
    

    print(generated_cqs)
    return generated_cqs,lines

def BERTScoreBinding(generated_cqs,true_cqs):
    cosine_scores = find_cosine_distances(true_cqs,generated_cqs)
    BERTScore = greatest_similatirty(cosine_scores)
    bindings = most_similar_object(cosine_scores)

    return BERTScore, bindings


def cq_coverage(true_cqs,model):
    print('cqs in cq_coverage' + str(true_cqs))
    generated_cqs,lines = generate_questions_from_csv(read_csv_to_data_frame('extracted_triplets/ontology_triplets.csv'),model)
    greatest_similarity_cqs,bindings = BERTScoreBinding(generated_cqs,true_cqs)
    addressed_cqs = [cq for cq, sim in zip(true_cqs, greatest_similarity_cqs) if sim < 0.5]
    lines_corresponding_to_addressed_cqs = [lines[a] for a in bindings]
    print(addressed_cqs)

    write_string_to_file('data/addressed_cqs/addressed_cqs.txt', str(addressed_cqs))
    
    return len(addressed_cqs)/len(true_cqs), lines_corresponding_to_addressed_cqs

def query_complexity(covered_cqs,triplets):
    nlp = spacy.load("en_core_web_lg")
    average = 0
    for entry in covered_cqs:
        doc = nlp(entry)
        subject = None
        object = None
        for token in doc:
    # Handle subjects
            if "subj" in token.dep_:
                subject_parts = [token]
                subject_parts.extend([child for child in token.children if child.dep_ in ("amod", "compound", "poss", "nummod", "det", "prep")])
                subject_parts = sorted(subject_parts, key=lambda x: x.i)  # Sort by token position
                subject = " ".join([t.text for t in subject_parts])
    # Handle objects
            if "obj" in token.dep_:
                object_parts = [token]
                object_parts.extend([child for child in token.children if child.dep_ in ("amod", "compound", "poss", "nummod", "det", "prep")])
                object_parts = sorted(object_parts, key=lambda x: x.i)
                object = " ".join([t.text for t in object_parts])

        print('this is the subject and object of the query:')
        print(subject)
        print(object)
        if subject != None and object != None:
            starting_point = nearest_neighbors(subject,triplets.iloc[:, 0].tolist())
            starting_point = (triplets.iloc[:, 0].tolist())[int(starting_point[0])]
            print('this is the starting point' + str(starting_point))
            ending_point = nearest_neighbors(object,triplets.iloc[:, 2].tolist())
            ending_point = (triplets.iloc[:, 2].tolist())[int(ending_point[0])]
            print('this is the ending point' + str(ending_point))
            shortest_path = find_shortest_path(triplets, starting_point, ending_point)
        if shortest_path is not None:
            print('this is the shortest path:')
            print(shortest_path)
            average += 1/len(shortest_path)
    print('this is the average closeness for the covered cqs:')
    print(average * 1/len(covered_cqs) if covered_cqs else 0)
    return average * 1/len(covered_cqs) if covered_cqs else 0
        
def find_shortest_path(df, start, end):

     # Build adjacency list
    adj = defaultdict(set)
    for _, row in df.iterrows():
        src = str(row[0])
        dst = str(row[2])
        adj[src].add(dst)

    # BFS for shortest path
    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        current, path = queue.popleft()
        if current == end:
            return path
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

