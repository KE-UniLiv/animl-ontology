from input_output import read_file_as_string
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import torch

np.random.seed(42)
torch.manual_seed(42)


def resource_name_extractor(generated_ontology, true_ontology,regex):
    generated_content = read_file_as_string(generated_ontology)
    true_content = read_file_as_string(true_ontology)


    generated_resources = list(set(re.findall(regex, generated_content)))
    true_resources = list(set(re.findall(regex, true_content)))

    print(generated_resources)
    print(true_resources)

    return generated_resources, true_resources

def greatest_similarity(generated_resources, true_resources):
    
    model = SentenceTransformer('all-mpnet-base-v2')
    generated_embeddings = model.encode(generated_resources, convert_to_tensor=True)
    true_embeddings = model.encode(true_resources, convert_to_tensor=True)

    similarities = cosine_distances(generated_embeddings, true_embeddings)

    greatest_similarity = []

    for row in similarities:
        greatest_similarity.append(float(np.min(row)))

    return greatest_similarity
    
def similarity_distribution(similarities):
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


def eurecom_baseline():
    class_regex = r'<(?:owl:Class|rdf:Description|rdfs:subClassOf)[^>]*?(?:rdf:about|rdf:resource)="[^"#]+[#/]([^"#/>]+)"'
    property_regex = r'<(?:rdf:Description|owl:ObjectProperty)[^>]*rdf:about="[^"#]+[#/]([^"#/>]+)"'

    generated_classes, true_classes = resource_name_extractor('ontologies/ontology.txt', 'musicmeta.txt', class_regex)
    greatest_similarity_classes = greatest_similarity(generated_classes, true_classes)
    similarity_dist_classes = similarity_distribution(greatest_similarity_classes)

    print('distribution of class names similarity:')
    print(f'Identical: {similarity_dist_classes[0]:.2f}%') 
    print(f'Likely Synonym: {similarity_dist_classes[1]:.2f}%')
    print(f'Likely Related Concept: {similarity_dist_classes[2]:.2f}%')
    print(f'Unrelated: {similarity_dist_classes[3]:.2f}%')

    generated_properties, true_properties = resource_name_extractor('ontologies/ontology.txt', 'musicmeta.txt', property_regex)
    greatest_similarity_properties = greatest_similarity(generated_properties, true_properties)
    similarity_dist_properties = similarity_distribution(greatest_similarity_properties)

    print('distribution of property names similarity:')
    print(f'Identical: {similarity_dist_properties[0]:.2f}%') 
    print(f'Likely Synonym: {similarity_dist_properties[1]:.2f}%')
    print(f'Likely Related Concept: {similarity_dist_properties[2]:.2f}%')
    print(f'Unrelated: {similarity_dist_properties[3]:.2f}%')

