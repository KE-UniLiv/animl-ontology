from rdflib import Graph

g = Graph()
g.parse("infinite.ttl", format="turtle")  # or "xml", "nt", etc.
print(f"Loaded {len(g)} triples.")

for s, p, o in g:
    print(f"Subject: {s}, Predicate: {p}, Object: {o}")

