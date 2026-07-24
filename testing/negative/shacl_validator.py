from pyshacl import validate
from rdflib import Graph

# ---------------------------------------------------------
# 1. Load RDF data from TTL file
# ---------------------------------------------------------
data_graph = Graph()
data_graph.parse("validation_ontology_acceptable.ttl", format="turtle")

# ---------------------------------------------------------
# 2. Load SHACL shapes from template and inject placeholder
# ---------------------------------------------------------
with open("shape.ttl", "r") as f:
    template = f.read()

# Example: dynamically insert a SPARQL constraint


# Load shapes into an RDFLib graph
shapes_graph = Graph()
shapes_graph.parse(data=template, format="turtle")

# ---------------------------------------------------------
# 3. Run SHACL validation (supports SHACL-SPARQL)
# ---------------------------------------------------------
conforms, results_graph, results_text = validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",          # optional
    abort_on_first=False,
    allow_infos=True,
    allow_warnings=True,
    advanced=True,
)

# ---------------------------------------------------------
# 4. Output results
# ---------------------------------------------------------
#print("Conforms:", conforms)
#print("\nValidation Report:\n")
print(results_text)


bad_data_graph = Graph()
bad_data_graph.parse("validation_ontology_unacceptable.ttl", format="turtle")

# ---------------------------------------------------------
# 2. Load SHACL shapes from template and inject placeholder
# ---------------------------------------------------------

# ---------------------------------------------------------
# 3. Run SHACL validation (supports SHACL-SPARQL)
# ---------------------------------------------------------
conforms, results_graph, results_text = validate(
    data_graph=bad_data_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",          # optional
    abort_on_first=False,
    allow_infos=True,
    allow_warnings=True,
    advanced=True, 
)

# ---------------------------------------------------------
# 4. Output results
# ---------------------------------------------------------
#print("Conforms:", conforms)
#print("\nValidation Report:\n")
print(results_text)