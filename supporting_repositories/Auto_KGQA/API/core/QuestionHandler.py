from openai import OpenAI
from dotenv import load_dotenv
import os
import sys
import warnings
import re
import os
# from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','..')))
from supporting_repositories.Auto_KGQA.API.sparql.Utils import convertToTurtle, list_to_string_triples
from supporting_repositories.Auto_KGQA.API.sparql.Filter_Triples import Filter_Triples
from supporting_repositories.Auto_KGQA.API.nlp.parsers import *
from supporting_repositories.Auto_KGQA.API.context.ContextLLM import *
from supporting_repositories.Auto_KGQA.API.context.ContextLLM import build_discriminator_prompt
from supporting_repositories.Auto_KGQA.API.configs import NUMBER_HOPS,LIMIT_BY_PROPERTY,FILTER_GRAPH,RELEVANCE_THRESHOLD,MAX_HITS_RATE,PRINT_HITS,TEMPERATURE_TRANSLATE,TEMPERATURE_SELECT,TEMPERATURE_FINAL_ANSWER,USE_A_BOX_INDEX
from supporting_repositories.Auto_KGQA.API.core.Configs_loader import load_configs
from supporting_repositories.Auto_KGQA.API.configs import *
from supporting_repositories.Auto_KGQA.API.nlp.normalizer import *
from supporting_repositories.Auto_KGQA.API.sparql.Endpoint import Endpoint
from supporting_repositories.Auto_KGQA.API.index.import_index import *
from src.generator import call_generator


#OpenAI
load_dotenv()



class QuestionHandler:
    def __init__(self,model,endpoint,endpoint_t_box,t_box_index,normalizer,messagesTranslater=ContextTranslator(""),messagesNL=ContextNLGenerator(),generalConversation=ContextDialog(),messagesChooseBest = ContextChooseBestSPARQL(""),a_box_index=None,model_name="gpt-3.5-turbo-16k") -> None:
        self.endpoint = endpoint
        self.endpoint_t_box = endpoint_t_box
        self.t_box_index = t_box_index
        self.normalizer = normalizer
        self.messagesTranslater = messagesTranslater
        self.messagesNL = messagesNL
        self.generalConversation = generalConversation
        self.messagesChooseBest = messagesChooseBest
        self.a_box_index = a_box_index
        self.model_name = model_name
        self.embedding_function = model


    def getRelatedTriples(self,question,index,number_hops=NUMBER_HOPS,limit_by_property=LIMIT_BY_PROPERTY):
        # print("getRelatedTriples: "+question)
        matchs = parseText(question,index,self.normalizer,self.endpoint)
        triples = ""
        nodes = []
        properties = []
        for match in matchs:
            # print("match: "+str(match))
            if match['content']['?type'] == 'property':
                properties.append(match['content']['?term'])
            else:
                nodes.append(match['content']['?term'])
            triples+= self.endpoint.describe(match["content"]["?term"],number_hops,limit_by_property)
        return triples,nodes,properties

    def getRelevantGraph(self,question,number_hops=NUMBER_HOPS,limit_by_property=LIMIT_BY_PROPERTY,filter_graph= FILTER_GRAPH,last_question=None,use_a_box_index=USE_A_BOX_INDEX):
        self.endpoint.visited_nodes = set()
        needed_nodes = []
        needed_properties = []
        hist_questions = question
        if last_question != None:
            hist_questions = last_question+"\n "+question
        triples,needed_nodes,needed_properties = self.getRelatedTriples(hist_questions,self.t_box_index)
        if use_a_box_index and self.a_box_index != None:
            # print("a_box_index")
            triples2,nodes,properties= self.getRelatedTriples(hist_questions,self.a_box_index,number_hops,limit_by_property)
            needed_nodes += nodes
            triples+= triples2
        # print("needed_nodes:"+str(needed_nodes))
        # print("needed_properties:"+str(needed_properties))
        triples+= self.endpoint_t_box.get_all_triples() #Put all relevant T-Box's triples in the selected triples set
        if filter_graph and len(triples) > 0:
            # print(triples)#aqui
            filter_triples = Filter_Triples(triples,self.embedding_function,relevance_threshold = RELEVANCE_THRESHOLD, max_hits_rate=MAX_HITS_RATE)
            selected_triples = filter_triples.filter_triples_relevance(question, print_hits=PRINT_HITS,needed_nodes=needed_nodes,needed_properties=needed_properties)
            triples = list_to_string_triples(selected_triples)
        # print("triples:\n"+triples)
        ttl = convertToTurtle(triples)
        self.endpoint.visited_nodes = set()
        return ttl
    

    def textToSPARQL(self,question,ttl,rag=None):
        self.messagesTranslater.changeGraph(ttl,rag=rag)
        self.messagesChooseBest.changeGraph(ttl)
        self.messagesTranslater.add({"role":"user","content":question})
        self.generalConversation.add({"role":"user","content":question})
        # print(self.messagesTranslater.to_list())
        #client = OpenAI()
        completion = call_generator('gpt',build_discriminator_prompt(question,ttl),n=1,temperature=0.9)
        coveredness = (m := re.search(r'\b(?:True|False)\b', completion.choices[0].message.content)) and m.group().lower()
        print(coveredness)
        if (coveredness == 'True') or (coveredness == 'true'):
            completion = call_generator('gpt',self.messagesTranslater.to_list(),n=5,temperature=TEMPERATURE_TRANSLATE)
            print('these are the candidate messages -----------------' + str(completion))
            results = []
            sparqls = []
            structured_results = []
            for choice in completion.choices:
                sparql = self.extractSPARQL(choice.message.content)
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    try:
                        question_formulated,query_results = self.endpoint.struct_result_query(sparql)
                        if not query_results  is None:
                            structured_results.append(question_formulated)
                            results.append(query_results)
                            sparqls.append(sparql)
                    except:
                        continue
                        
            if len(results) > 0:

                self.messagesChooseBest.changeQuestion(question,structured_results)
                completion = call_generator('gpt',self.messagesChooseBest.to_list(),temperature=TEMPERATURE_SELECT)
                selection = completion.choices[0].message.content
                try:
                    selection_number = [int(s) for s in re.findall(r'-?\d+', selection)] [0]
                except:
                    selection_number = -1
                print('the selection is' + str(selection_number))
                if selection_number == -1:
                    sparql_selected = """
                        this question was not answered correctly
                     """
                    results_selected = []
                else:
                    sparql_selected = sparqls[selection_number]

                self.messagesTranslater.add({"role":"assistant",
                     "content":f"""
                        ```sparql
                            {sparql_selected}
                           ```
                        """
                    })      
            else: 
                self.messagesTranslater.add({"role":"assistant",
                                             "content":""})
                return [[],[],'none of the generators outputs were valid sparql']
            return [sparqls,results,sparql_selected]
        else:
            return [[],[],'our discriminator agent believes that this cq is not covered']
    



    def generateNLResponse(self,question,sparql_selected,results_selected):
        question_forumlated = f"""
        User question: "{question}";
        SPARQL query:
        ```sparql
        {sparql_selected}
        ```;
        JSON result set:
        ```json
        {results_selected}
        ```;
        """
        self.messagesNL.add({"role":"user","content":question_forumlated})
        completion = call_generator('gpt',self.messagesNL.to_list(),temperature=TEMPERATURE_FINAL_ANSWER)
        answer = completion.choices[0].message.content
        self.messagesNL.add({"role":"assistant","content":answer})
        if self.generalConversation[-1]["role"] == "assistant":
            self.generalConversation[-1]["content"] = self.generalConversation[-1]["content"] + f"\nSPARQL:```sparql\n{sparql_selected}```\n{answer}"
        else:
            self.generalConversation.add({"role":"assistant","content":f"\nSPARQL:```sparql\n{sparql_selected}```\n{answer}"})
        return answer
    

    def processQuestion(self,question,number_hops=NUMBER_HOPS,limit_by_property=LIMIT_BY_PROPERTY,filter_graph= FILTER_GRAPH,last_question=None):
        ttl = self.getRelevantGraph(question,number_hops,limit_by_property,filter_graph,last_question=last_question)
        textToSPARQL_return = self.textToSPARQL(question,ttl)
        if textToSPARQL_return != None:
            sparqls,results,sparql_selected = textToSPARQL_return
            #answer = self.generateNLResponse(question,sparql_selected,results_selected)
            llmAnswer = {'question':question,
                         'sparql':sparql_selected,
                         'fragments':ttl,
                         'sparqls':sparqls}
            return llmAnswer
        else:
            print("Não gerou consulta SPARQL válida")
            self.generalConversation.add({"role":"user","content":question})
            completion = call_generator('gpt',self.generalConversation.to_list(),temperature=1.0)
            answer = completion.choices[0].message.content
            self.generalConversation.add({"role":"assistant","content":answer})
            return {'answer':answer,
                    'question':question,
                    'sparql':None,
                    'fragments':ttl,
                    'sparqls':None}

    @staticmethod
    def extractSPARQL(text):
        searchSPARQL = re.search("```(.|\n)*```",text)
        if searchSPARQL is None:
            return ''
        start,end = searchSPARQL.span()
        sparql = text[start:end]
        sparql = sparql.replace("```sparql","").replace("```","")
        return sparql


    @staticmethod
    def printAnswer(llmAnswer):
        if llmAnswer['sparql'] is not None:
            finalAnswer = f"""User: {llmAnswer['question']}\nGPT: {llmAnswer['answer']}\n\n\n\nSPARQL:\n{llmAnswer['sparql']}\n-------------------------------------------------------------\n"""
        else:
            finalAnswer =f"""User: {llmAnswer['question']}\nGPT: {llmAnswer['answer']}\n-------------------------------------------------------------\n"""
        #print(finalAnswer)

def run_question(question,model):
    normalizer, endpoint_t_box, t_box_index, endpoint_a_box, a_box_index = load_configs(model)
    Handler = QuestionHandler(model,Endpoint(ENDPOINT_KNOWLEDGE_GRAPH_URL),endpoint_t_box,t_box_index,normalizer,a_box_index=a_box_index,)
    result = Handler.processQuestion(question)
    print(' it terminated without error')
    print('that ')
    return result