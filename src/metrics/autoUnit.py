import sys
import os
import subprocess
import nltk
from langchain_community.embeddings import SentenceTransformerEmbeddings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.input_output import save_to_csv, overwrite_first_line, read_lines_from_file, write_string_to_file, save_array_to_file
from supporting_repositories.Auto_KGQA.API.create_indexes import createIndexes
from supporting_repositories.Auto_KGQA.API.core.QuestionHandler import run_question


def autoUnit(parameters,thread_number,output_queue):
    if parameters['initialisation_step'] == 1:

        nltk.download('punkt')
        overwrite_first_line("supporting_repositories/Auto_KGQA/API/configs.py",f'ENDPOINT_KNOWLEDGE_GRAPH_URL = "animl_ontology/data/ontologies/{parameters['ontology']}.ttl"')
        createIndexes()
        parameters['model'] = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        parameters['paralleism_blocker'] = False
        print('skideedle skidoodle your arms are now a noodle')
        output_queue.put(parameters)
    else:
        cqs = read_lines_from_file(f'data/input_cqs/{parameters['ontology']}.txt')
        average = 0
        library = []
        for cq in cqs:
            print('the question is being run')
            result = run_question(cq,parameters['model'])
            print(result['sparql'])
            write_string_to_file(f'supporting_repositories/OWLUnit/tests/{(cq[:-1].replace(' ','_')).replace('/','_')}_{thread_number}.ttl',f'''
            @prefix owlunit: <https://w3id.org/OWLunit/ontology/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix owlunittest: <https://w3id.org/OWLunit/test/> .

            owlunittest:primary  a owlunit:CompetencyQuestionVerification ;
 	            owlunit:hasCompetencyQuestion "{cq}" ;
 	            owlunit:hasSPARQLUnitTest """
	            {result['sparql']}""" ;
	            owlunit:testsOntology <../../../data/ontologies/{parameters['ontology']}.ttl> .''')
        
            print("Current working directory:", os.getcwd())
            output = subprocess.run(["java", "-jar", 'supporting_repositories/OWLUnit/OWLUnit-0.3.2.jar', "--test-case", "https://w3id.org/OWLunit/test/primary","--filepath",f"supporting_repositories/OWLUnit/tests/{(cq[:-1].replace(' ','_')).replace('/','_')}_{thread_number}.ttl"], capture_output = True)
            print(output)
            if str(output).__contains__('PASSED'):
                average += 1
                result['correctness'] = True
            else:
                result['correctness'] = False
            print(result['correctness'])
            library.append({'question':result['question'],'correctness':result['correctness']})
        average = average/len(cqs)
        print(average)
        output_queue.put(average)
        save_array_to_file(library,f'data/addressed_cqs/{parameters['ontology']}.txt')