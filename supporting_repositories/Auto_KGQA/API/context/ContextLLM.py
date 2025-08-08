import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from API.configs import SIZE_CONTEXT_WINDOW_TRANSLATE, SIZE_CONTEXT_WINDOW_SELECT, SIZE_CONTEXT_WINDOW_FINAL_ANSWER,VISUALIZATION_TOOL_URL
class ContextDialog:
    def __init__(self,length=7,language="en"):
        self.system = []
        self.content = []
        self.maxLength = length
        self.language = language

    def add(self,item):
        if len(self.content) > self.maxLength:
            self.content.pop(0)
        self.content.append(item)

    def to_list(self):
        return self.system + self.content
    
    def __len__(self):
        return len(self.content)
    
    def __getitem__(self, i): 
        return self.content[i]
    
    def __setitem__(self, i, v):
        self.content[i] = v
    def __str__(self):
        return str(self.system + self.content)


original_discriminator_prompt = """you are an ontology engineer
    You are asked to infer if the ontology described at the bottom of the prompt can address
     the competency question above it

     in order to fully address a competency question the ontology must be able to

        model all the relationships and conditions mentioned,
        and otherwise express the entire question without simplification

    please respond True for expressable questions, and False otherwise
    """

complexity_discriminator_prompt = """you are an ontology engineer
    You are asked to infer if it is feasible for an LLm based system to fully map the provided question
    to a sparql query upon the provided ontology

     in order to do this well you should consider

        how many entities are involved
        if any of the relationships denoted in the question are implicit or reified in the ontology
        the general complexity of the statement 

    please respond True for expressable questions, and False otherwise
    """
    
def build_discriminator_prompt(question,graph):
    discriminator_prompt = f"{complexity_discriminator_prompt}  {f' question: {question} ontology: {graph}'}"
    print(discriminator_prompt)
    return discriminator_prompt
    



original_restriction  = """
    - Use only classes and properties defined in the RDF graph, for this is important to use the same URIs for the properties and classes as defined in the original graph;
    - Include all the the prefixes used in the SPARQL query;
    - Declare non-essential properties to the question as OPTIONAL if needed;
    - DO NOT use specific resources in the query;
    - Declare filters on strings (like labels and names) as filters operations over REGEX function using the case insensitive flag."""

generalisation_restriction  = """
    - Use only classes and properties defined in the RDF graph, for this is important to use the same URIs for the properties and classes as defined in the original graph;
    - Include all the the prefixes used in the SPARQL query;
    - Declare non-essential properties to the question as OPTIONAL if needed;
    - DO NOT use specific resources in the query;
    - Declare filters on strings (like labels and names) as filters operations over REGEX function using the case insensitive flag.
    - Do not include foundational concepts like Thing
    - you must not ignore any of the logical restrictions expressed by the cq in order to make your query work, nor otherwise create query expressinhg a simplified version of the question
        - for example, if a cq asks 'what is a companies most popular product' you may not write a query that simply returns all their products
    
    - if you cannot follow all of these rules and still produce a valid sparql query, simply return 'I cannot answer this question'"""

inaccuracy_accepting_restriction = """
    - where possible you should use the classes and properties defined in the RDF graph, however (only when it is impossible to reasonably approximate the original question with existing resources) you may invent new classes and properties to use in your query;
    - when using existing classes and properties it is important to use the same URIs for the properties and classes as defined in the original graph;
    - Include all the the prefixes used in the SPARQL query;
    - Declare non-essential properties to the question as OPTIONAL if needed;
    - DO NOT use specific resources in the query;
    - Declare filters on strings (like labels and names) as filters operations over REGEX function using the case insensitive flag."""

class ContextTranslator(ContextDialog):
    restrictions = generalisation_restriction
    def __init__(self,graph,length=SIZE_CONTEXT_WINDOW_TRANSLATE,language="en"):
        super().__init__(length,language)
        self.changeGraph(graph)
    
    def changeGraph(self,graph,rag=None):
        self.system = []
        rag_text = ""
        if rag:
            rag_text = "Here are some sample related questions accompanied by their queries to help you:\n"+rag+"\n"
        if self.language == "en":
            self.system.append({"role":"system","content":"Consider the following RDF graph written in n3 syntax: "+str(graph)})
            # self.system.append({"role":"system","content":"""Write a SPARQL query for the question given by the user using only classes and properties defined in the RDF graph, for this is important to use the same URIs for the properties and classes as defined in the original graph. Also remember to include the prefixes. Moreover declare non-essential properties to the question as OPTIONAL if needed. Declare filters on strings (like labels and names) as filters operations over REGEX function using the case insensitive flag, for example use '''?a rdfs:label ?name. FILTER(REGEX(?name,"[VALUE NAME]","i"))''' instead of '''?a rdfs:label "[VALUE NAME]".''' ."""})
            self.system.append({"role":"system","content":f"""Write a SPARQL query for the question given by the user following the restrictions: \n{self.restrictions}
Example:
    Question: 'Who is Caio?'
    Answer: ```sparql
        SELECT ?caio ?name WHERE{{
            ?caio rdfs:label ?name.
            FILTER(REGEX(?name,"Caio","i"))
        }}```
{rag_text}                    """})
        elif self.language ==  "pt":
            self.system.append({"role":"system","content":"Considere o seguinte grafo RDF escrito na sintaxe Turtle: "+str(graph)})
            self.system.append({"role":"system","content":"""Escreva uma consulta SPARQL para a questão dada pelo usuário utilizando apenas classes e propriedades definidas no grafo RDF, para isso é importante utilizar as mesmas URIs para as propriedades e classes como definidas no grafo original. Também é importante lembrar de incluir os prefixos. Além disso, declare propriedades não essenciais para a questão como como OPTINAL se necessárias. Declare filtros sobre strings (como labels e nomes) como operações de filtros sobre funções REGEX usando a flaf case insensitive, por exemplo use '''?a rdfs:label ?name. FILTER(REGEX(?name,"[VALUE NAME]","i"))''' ao invés de '''?a rdfs:label "[VALUE NAME]".'''"""})


def build_original_best_selection(question,structured_results):
        prompt_best_selection = f"""
        Given the question: "{question}"
        Select the number of the option that better representes a SPARQL query for the given question:
        ```json
        {{"""

        for idx,structured_result in enumerate(structured_results):
            prompt_best_selection+= f"""{idx}:{structured_result},\n"""
        
        prompt_best_selection+= f"""}}```
        Use the following criteria to evaluate the options: {original_restriction}
        Return only the number of the selected option and nothing more!"""
        # print(prompt_best_selection)

        return prompt_best_selection

def build_inaccuracy_accepting_best_selection(question,structured_results):
        prompt_best_selection = f"""
        Given the question: "{question}"
        determine whether any of the given sparql queries and sufficient to completley answer an unsimpliefed version of the question:
        ```json
        {{"""

        for idx,structured_result in enumerate(structured_results):
            prompt_best_selection+= f"""{idx}:{structured_result},\n"""
        
        prompt_best_selection+= f"""}}```
        if none are acceptable in this way then return the number -1,

        otherwise,
        Select the number of the option that better representes a SPARQL query for the given question

        Use the following criteria to evaluate the options: {ContextTranslator.restrictions}
        Return only the number of the selected option and nothing more!"""
        # print(prompt_best_selection)

        return prompt_best_selection


def build_(question,structured_results):
        prompt_best_selection = f"""
        Given the question: "{question}"
        determine whether any of the given options represent an accpetable sparql query for the given question:
        ```json
        {{"""

        for idx,structured_result in enumerate(structured_results):
            prompt_best_selection+= f"""{idx}:{structured_result},\n"""
        
        prompt_best_selection+= f"""}}```
        if none are acceptable then return the number -1,

        otherwise,
        Select the number of the option that better representes a SPARQL query for the given question

        Use the following criteria to evaluate the options: {ContextTranslator.restrictions}
        Return only the number of the selected option and nothing more!"""
        # print(prompt_best_selection)

        return prompt_best_selection

class ContextChooseBestSPARQL(ContextDialog):
    def __init__(self,length=SIZE_CONTEXT_WINDOW_SELECT):
        super().__init__(length)
        
    def changeGraph(self,graph):
        self.system = []
        self.system.append({"role":"system","content":"Consider the following RDF graph written in Turtle syntax: "+str(graph)})

    def changeQuestion(self,question,structured_results):
        self.system.append({"role":"system","content":build_original_best_selection(question,structured_results)})


     
        
        
class ContextNLGenerator(ContextDialog):
    def __init__(self,length=SIZE_CONTEXT_WINDOW_FINAL_ANSWER,language="en"):
        super().__init__(length,language)
        if self.language == "en":
            self.system.append({"role":"system","content":f"""Use the SPARQL query and its result set as JSON object to write a answer to the user question.
                                Here are some points that you should follow in the generated response: 
                                    - DO NOT explain neither cite the SPARQL query and JSON in yours response;
                                    - Show the URIs of the objects you use in your response, minus the URIs of datatypes; 
                                    - Format all the URIs in your response in the markdown notation, e.g. [URI](URI);
                                    - If the URL is not an image, add the following prefix to URI links: {VISUALIZATION_TOOL_URL}, e.g. [http://example.com]({VISUALIZATION_TOOL_URL}http://example.com)
                                """})
        elif self.language ==  "pt":
            self.system.append({"role":"system","content":"Use a consulta SPARQL e seu conjunto de resultados como um objeto JSON para responder a questão do usuário"})
