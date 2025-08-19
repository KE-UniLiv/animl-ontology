# animl-ontology
The Analytical Information Markup Language (AnIML) Ontology

## Alignments 🎯

To further enrich the AnIML Ontology, we provide alignments through state-of-the-art models and approaches supported through the libraries [`DeepOnto`](https://krr-oxford.github.io/DeepOnto/) and [`OntoAligner`](https://ontoaligner.readthedocs.io/). Alignments are done between the [`AniML`](alignment/ontologies/AniML/anitology.rdf) Ontology and the [`Allotrope`](https://www.allotrope.org/ontologies) Ontology.

| Aligner  | Approach                     | Library     |
| -------- | ---------------------------- | ----------- |
| ConvE    | Knowledge Graph Embeddings   | OntoAligner |
| CompGCN  | Knowledge Graph Embeddings   | OntoAligner |
| TransE   | Knowledge Graph Embeddings   | OntoAligner |
| RotatE   | Knowledge Graph Embeddings   | OntoAligner |
| DistMult | Knowledge Graph Embeddings   | OntoAligner |
| ComplEx  | Knowledge Graph Embeddings   | OntoAligner |
| LogMap   | Hybrid                       | DeepOnto    |
| BERTmap  | Hybrid (via [`BERT`](https://huggingface.co/docs/transformers/en/model_doc/bert) embeddings) | DeepOnto    |

The outputs for these mappings are available [`here`](/alignment/outputs/), a summary [`excel file`](/alignment/outputs/summary.xlsx) is also provided.
