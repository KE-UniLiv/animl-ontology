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

    When you're done send me only the whole ontology you've designed in turtle syntax, not including any text outside of the ontology"""

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