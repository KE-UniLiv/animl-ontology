from deeponto.onto import Ontology
from deeponto.onto.projection import OntologyProjector

def LLM_query_complexity(addressed_cqs, model,list_of_cq_bindings):
    onto = Ontology('data/ontologies/ontology.txt')
    output = Ontology.get_all_axioms(onto)
    print(output)

LLM_query_complexity(None,None,None)