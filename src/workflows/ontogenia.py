from src.input_output import read_file_as_string
from prompts import ontogenia, user_prompt
from src.generator import call_generator

def Ontogenia(parameters,cqs):
    print('Ontogenia workflow started--------------------------------------------------------------------')
   # print('starting with parameters:' + str(parameters))

    if parameters[len(parameters)-1] == -1:
        batches = []
        for i in range(0, len(cqs), parameters[0]):
            batches.append(str(cqs[i:i + parameters[0]]))
        parameters.insert(-1, batches)
        parameters.insert(-1, [])
        parameters[len(parameters)-1] = 0
        return '',parameters
    elif parameters[len(parameters)-1] == 0:
        print(len(parameters[2]), len(parameters[3]))
        if len(parameters[2]) > len(parameters[3]):
            parameters[3].append(parameters[2][len(parameters[3])])
            fragment = call_generator(user_prompt+str(parameters[3]), (f"""Define an ontology using an overall procedure based on understanding each competency 
                                   question using this procedure: {ontogenia}   basing on the procedure, and following the previous output 
                                   {read_file_as_string('ontologies/ontology.txt')}
                                    design an ontology that comprehensively answers the compentecy questions passed to you in the user prompt
                                    When you're done send me only the whole ontology you've designed in OWL format, without any comment outside the OWL)"""),parameters[1])
            return fragment,parameters
        else:
            parameters[len(parameters)-1] = 1
            return read_file_as_string('ontologies/ontology.txt'),parameters