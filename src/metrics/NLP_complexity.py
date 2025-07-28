import spacy
from collections import deque, defaultdict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.evaluator import nearest_neighbors

# somewhat useful, unknown level of error due to NLP.

def query_complexity(covered_cqs,triplets):
    nlp = spacy.load("en_core_web_lg")
    average = 0
    shortest_paths = []
    for entry in covered_cqs:
        print('this is the query: ' + entry)
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
            shortest_paths.append(shortest_path)
        else:
            shortest_paths.append(None)
    return (average * 1/len(covered_cqs) if covered_cqs else 0), shortest_paths
        
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