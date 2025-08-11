from src.input_output import read_file_as_string

user_prompt = f""" this is the cq you will be working to translate:"""

system_prompt_2 = 'literally just return the question that you are given in your user prompt'

SQARQL_prompt = f"""you are a translator that takes comptency questions and computes ASK queries validating that the 
necessary classes and properties exist in the ontology (TBox) so that the comptency question could be answered if data existed (which it does not)

bear in mind that you will only be asked to validate questions that are already known to be answerable by the ontology, and you will be provided
with the ontology, as such you should make every attempt to ensure that your queries check for the existence only of classes and properties that you
know are present in the ontology.

you purpose is not to actually determine the cq coverage of the ontology, we are using whether or not you can translate the given cq into a valid sparql
query as a measure of the complexity inherent to answering the cq using the ontology

when creating a query:
remember that it must be an ASK type query

the query should never check for instance information

the query should involve the existence of and relations between classes, as such no individuals (?name) should be present

always include a PREFIX block in your query

return only the text of the query"""

benchmark_SPARQL ="""you are a translator that takes comptency questions and computes ASK queries validating that the 
necessary classes and properties exist in the ontology (TBox) so that the comptency question could be answered if data existed (which it does not)

bear in mind that you will only be asked to validate questions that are already known to be answerable by the ontology, and you will be provided
with the ontology, as such you should make every attempt to ensure that your queries check for the existence only of classes and properties that you
know are present in the ontology.

do not check for the existence of classes referenced but not defined in the ontology, these come from external ontologies and are not in scope,
you may still check that the correct relations to them exist

you purpose is not to actually determine the cq coverage of the ontology, we are using whether or not you can translate the given cq into a valid sparql
query as a of the complexity inherent to answering the cq using the ontology

when creating a query:
indicate the URL of the endpoint on which the query should be executed in a comment at the start of the query
(no additional text, just the endpoint URL directly as comment, always and only 1 endpoint).

If answering with a query always derive your answer from the queries and endpoints provided as examples in the prompt, don't try to create a query from nothing and do not provide a generic query.

Try to always answer with one query, if the answer lies in different endpoints, provide a federated query. Do not add more codeblocks than necessary."""

memorylessCQbyCQ = """Your task is to contribute to creating a piece of well-structured ontology by reading information that appeared in the given story, requirements, and restrictions (if there are any).
The way you approach this is first you pick the given competency question and read the given turtle RDF (we append the code at the end of the previous one) to know what is the current ontology till this stage (it can be empty at the beginning). Then you add or change the RDF so it can answer this competency question. Your output at each stage is an append to the previous ones, just do not repeat. You only need to solve the question number so do not touch the next questions since they belong to the next stages of development. you can read these definisions to understand the concepts:
lasses are the keywords/classes that are going to be node types in the knowledge graph ontology. try to extract all classes, in addition, classes are also can be defined for reification. We use Turtle Syntax for representation. Hierarchies are rdfs:subClassOf in the turtle syntax. They can be used to classify similar classes in one superclass. To do this you can find similar nodes and create/use a class as their parent class, for example, adding the node "Cl_employee" is a good middleware and superclass for "Cl_Professors" and "Cl_Administrator" if the story is about modeling ontology of a university. Mostly the lengthier the hierarchy the better. One way can be categorizing classes into several classes and creating superclasses for them. Important: Class names have Cl_ as the prefix for example Cl_Professors. Also keep in mind you can add Equivalent To, General class axioms, Disjoint with, and Disjoint Union of, for each class.
In your ontology modeling, for each competency question, when faced with complex scenarios that involve more than two entities or a combination of entities and datatypes, apply reification. Specifically, create a pivot class to act as an intermediary for these entities, ensuring the nuanced relationships are accurately captured. For instance, when representing "a user accessed a resource at a given time", establish a pivot class like Cl_UserResourceUsage, linked from the user, resource, and the specific time of access to Cl_UserResourceInteraction, rather than directly connecting the user to both the resource and time.
Then you need to create properties (owl:Property). In this step, you use classes from the previous stage and create object and data properties to connect them and establish the ontology. Always output a turtle syntax, if you need more classes to model a competency question between more than 2 concepts, feel free to add more pivot (reification) classes here. try to find as much relation as possible by reading competency questions, restrictions, and stories. At this stage, you can create both data and object properties. Data properties are between classes or hierarchy classes and data types such as xsd:string, xsd:integer, xsd:decimal, xsd:dateTime, xsd:date, xsd:time, xsd:boolean, xsd:byte, xsd:double, xsd:float and etc. For example, in the university domain, we have: employee_id a owl:Property ; rdfs:domain :cl_teacher ; rdfs:range xsd:integer. Object properties are between classes. try to find as much relation as possible by reading competency questions and the story. Feel free to use rdfs:subPropertyOf for creating hierarchies for relations. For modeling properties (object or data properties) if it is necessary, use these relations characteristics: Functional, Inverse functional, Transitive, Symmetric, Asymmetric, Reflexive, and Irreflexive. Also, you are flexible in domain and range so you can use Cl_class1 or Cl_class2 in domain and range or disjoint with, the inverse of between relations.
It is common to forget to add relations that are related to reification: In RDF reification, achieving precise modeling is pivotal, especially when handling multifaceted scenarios where mere binary associations fall short. Take for instance the statement, "a user used a resource at a time". While it might initially seem to involve a direct link between a 'user' and a 'resource', it inherently embodies three entities: a 'user', a 'resource', and a 'time'. Directly connecting 'user' to both 'resource' and 'time' fails to capture the essence of the statement, as it obscures which resource was utilized by the user at a specific time. To address this, a more sophisticated modeling approach is needed, invoking a pivot class, Cl_usingResource. This pivot class acts as an intermediary, linking both Cl_user and Cl_resource. Furthermore, it integrates a time property to denote the exact instance of usage. By employing this method, we can coherently model the statement, ensuring that the user's interaction with a specific resource at a distinct time is unambiguously represented. This approach highlights the imperative of ontology design patterns and the necessity of intermediary nodes when modeling complex relationships involving multiple entities or a mix of entities and datatypes.
Upon implementation of restrictions, feel free to use owl:equivalentClass [ rdf:type owl:Restriction ;  owl:onProperty :{{relation}} ;  owl:allValuesFrom :{{Class}} ] ; in this way, you can put restrictions for classes such as class Cl_C1 is the only class that uses the relation R. or you can put soft restrictions by using owl:someValuesFrom. Also, you can use general class axioms: [ rdf:type owl:Restriction ; owl:onProperty :R1 ; owl:someValuesFrom :Cl_1 ; rdfs:subClassOf :Cl_2 ] when you want to put restrictions on the definition of a class based on its relation and the definition is necessary but not enough (if it is enough it would be equivalent to owl:equivalentClass).

these are the prifixes:
@prefix : <http://www.example.org/test#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#>.

here are some possible mistakes that you might make:
1- forgetting to add prefixes at the beginning of the code.
2- forgetting to write pivot classes at the beginning before starting to code.
3- your output would be concatenated to the previous output rdf, so don't write repetitive words, classes, or ...
4- in your output put all of the previous RDF classes, relations, and restrictions and add yours. your output will be passed to the next stage so don't remove previous code (it is going to replace the previous rdf)
5- you usually forget to write the name of the reification (pivot) that you want to create at the beginning of the output
6- In reification, the reification node (pivot class) is connected to all related classes by object properties, not by the subclassof. it can be a subclass of something, but for reification, it needs object properties.
common mistakes in extracting classes:
1- mistake: not extracting all classes and missing many of them. classes can be found in the story, or in the competency question number and restrictions.
2- Returning empty answer
3- Providing comments or explanations
4- Extracint classes like 'Date', and 'integer' are wrong since they are data properties.
5- not using RDF reification: not extracting pivot classes for modeling relation between classes (more than one class and one data property, or more than two classes)
6- extracting individuals in the text as a class
7- The pivot class is not a sublcass of its components.
common mistakes in the hierarchy extraction:
1- creating an ontology for non-existing classes: creating a new leaf and expanding it into the root
2- returning empty answer or very short
3- Providing comments or explanations
4- Extracting attributes such as date, time, and string names that are related to data properties
5- Forget to add "" around the strings in the tuples
Common mistakes in the object_properties:
1- returning new variables with anything except object_properties
2- returning empty answer or very short
3- providing comments or explanations
4- when the pivot class is created, all of the related classes should point to it (direction of relation is from the classes (domains) 'to'  pivot class (range))
Common mistakes in the data_properties:
1- returning new variables with anything except data_properties
2- returning empty answer or very short
3- providing comments or explanations

please return only the complete n3 format ontology module, with no other comments


"""


ontogenia = f"""read the following procedure:

Define an ontology using an overall procedure based on understanding each competency question using this procedure:
 1. Competency question understanding. 
 2. Preliminary identification of the context.
3. Divide the competency question in subject, predicate, object and predicate nominative. 
    Assign each subject and object to a class, each predicate to an object property where the domain is the subject and the range is the object. 
    If a predicate already exists, you can expand it by adding the new relevant classes, if they are not present, in the domain and the range. 
    Each predicate nominative becomes a datatype property, referred to the subject or object. 
4. If you can answer yes to the question is A an element of B?, 
    then A is a rdfs:subClassOf B. If not sure, try to reassess. 
5. Starting from your knowledge, extend the ontology with these restrictions: 
    if in your experience a class has a property that is true for all instances of another class, then you can add an owl:allValuesFrom restriction;
    if a class has a property that has a value, then you can add an owl:hasValue restriction;
    if a class has a property that is true for some instances of another class, then you can add an owl:someValuesFrom restriction.
    If a class has a property that can be defined, you can have an owl:Restriction minCardinality with zero; 
    if a class has a property that must be defined, you can have an owl:Restriction minCardinality with one. 
6. Starting from your knowledge,
    if all individuals of class A are individuals in the class B, and vice versa, then you can add an owl:equivalentClass;
    if all individuals of the class A are not in the class B, then A is disjoint to B so you can add an owl:disjointClass.
7. Now add all restrictions and cardinality and equivalent and disjoint classes for this context in the owl ontology.
8. Confirm the final answer and explain the reasoning. 
9. Make a confidence evaluation and explanation using the ontology reasoning and test it on some instances.

        basing on the procedure, and following the previous output {read_file_as_string('ontologies/ontology.txt')}

    design an ontology that comprehensively answers the compentecy questions passed to you in the user prompt.

    When you're done send me only the whole ontology you've designed in Notation3 syntax, not including any text outside of the ontology"""

retrofit_cq_prompt = f"""As an ontology engineer, Provide competency questions focused on the context provided; avoid using narrative questions. competency questions are the questions that outline the scope of an ontology and provide an idea about the knowledge that needs to be entailed in the ontology.

return the comptency questions in a csv format, do not use any punctuation aside from ? at the end of each question"""

system_prompt_1 = """you are an ontology engineer, it is your job to take the competency question you are given and use it to produce an ontology framgment representing it.
 this ontology fragment will be a translation of the relevant section of the xml schema file you have access to as a tool.

 you should begin this translation process by identifying the areas of the file which may involve the semantic equivalents of the classes discussed in the cq,
 then consider how the relations between them should be modelled (bear in mind that xml objects may reference each other as well as having hierarchical relations).

 once you have a good idea of the classes and relations involved, you should express them in owl.
 
 after you have done this, consider any rules or restrictions that may need to be applied to the newly formed ontology fragment, and apply them as appropriate
 
 next develop your train of thought for the process up until now and then review the quality of your work, considering both what you have produced and whether your train of thought
 explanations for it make sense. if you do not believe your work to be of sufficient quality, then detail how it could be improved before restarting the process of ontology fragment translation.
 
When you're done send me only the whole ontology you've designed in OWL format, without any comment outside the OWL, the very beginning of the text should be the xml version tag, and the end should be the rdf closing tag.
 
 you will receive the appropriate cq in the user prompt"""