from methods import get_ontologies, run_bertmap_direct, run_kge_ontoaligner, run_lightweight_ontoaligner, run_logmap_direct, run_llm_ontoaligner, run_rag_large_ontoaligner, run_retriever_ontoaligner
from ontoaligner.ontology import MouseHumanOMDataset, AniMLAllotropeOMDataset

import os
import questionary

# TODO, lazy load deeponto

if __name__ == "__main__":

    source_ontology_str = questionary.select(
        "Choose a source ontology",
        choices=["AnIML", "AnIML (Skeleton)", "FishS+", "FishS", "Allotrope", "MusicMeta", "TheMusicOntology", "mouse-human-source", "mouse-human-target"]
    ).ask()

    target_ontology_str = questionary.select(
        "Choose a target ontology",
        choices=["AnIML", "AnIML (Skeleton)", "FishT+", "FishT", "Allotrope", "MusicMeta", "TheMusicOntology", "mouse-human-source", "mouse-human-target"]
    ).ask()

    oamethod = questionary.select(
        "Choose an alignment method",
        choices=["logmap", "bertmap", 
                 "ontoaligner heavyweight", "ontoaligner lightweight", "ontoaligner retriever", "ontoaligner llm", "ontoaligner kge"]
    ).ask()

    typeof_lightweight = questionary.select(
        "Choose a type of lightweight alignment",
        choices=["Fuzzy", "WeightedFuzzy", "TokenSetFuzzy"]
    ).ask() if oamethod == "ontoaligner lightweight" else None

    typeof_retriever = questionary.select(
        "Choose a type of retriever alignment",
        choices=["SBERTRetrieval", "SVMBERTRetrieval (NOT WORKING)", "TFIDFRetrieval", "BM25Retrieval"]
    ).ask() if oamethod == "ontoaligner retriever" else None

    typeof_kge = questionary.select(
        "Choose a type of KGE alignment",
        choices=["ConvE", "TransD", "TransE", "DistMult", "ComplEx", "RotatE", "CompGCN"]
    ).ask() if oamethod == "ontoaligner kge" else None

    source_ontology = get_ontologies()[source_ontology_str]
    target_ontology = get_ontologies()[target_ontology_str]
    reference_ontology = os.path.join(os.getcwd(), "alignment", "ontologies", "mouse-human", "reference.xml")

    mousehumanref = get_ontologies()["mouse-human-reference"]
    fishref = get_ontologies()["fishref"]
    ## -- DeepOnto methods
    run_logmap_direct(source_ontology, target_ontology, os.path.join(os.getcwd(), "alignment", "outputs", "logmap", "logmap_mappings.xml")) if oamethod == "logmap" else None
    run_bertmap_direct(source_ontology, target_ontology) if oamethod == "bertmap" else None

    ## -- Ontoaligner methods
    run_rag_large_ontoaligner(source_ontology, target_ontology, reference_ontology, os.path.join(os.getcwd(), "alignment", "outputs", "ontoaligner", "ontoaligner_full_model_mappings.xml"), task=MouseHumanOMDataset()) if oamethod == "ontoaligner" else None
    run_lightweight_ontoaligner(source_ontology, target_ontology, reference_ontology, os.path.join(os.getcwd(), "alignment", "outputs", "ontoaligner", f"ontoaligner_lightweight_{typeof_lightweight}_{source_ontology_str}2_{target_ontology_str}_mappings.xml"), typeof_lightweight) if oamethod == "ontoaligner lightweight" else None
    run_retriever_ontoaligner(source_ontology, target_ontology, os.path.join(os.getcwd(), "alignment", "outputs", "ontoaligner", f"ontoaligner_retriever_{typeof_retriever}_{source_ontology_str}2_{target_ontology_str}_mappings.xml"), typeof_retriever, top_k=5) if oamethod == "ontoaligner retriever" else None
    run_llm_ontoaligner(source_ontology, target_ontology, os.path.join(os.getcwd(), "alignment", "outputs", "ontoaligner", f"ontoaligner_llm_{source_ontology_str}2_{target_ontology_str}_mappings.xml"), reference_ontology, task=MouseHumanOMDataset()) if oamethod == "ontoaligner llm" else None
    run_kge_ontoaligner(source_ontology, target_ontology, os.path.join(os.getcwd(), "alignment", "outputs", "ontoaligner", f"ontoaligner_kge_{typeof_kge}_{source_ontology_str}2_{target_ontology_str}_mappings.xml"), method=typeof_kge, referencepath=fishref) if oamethod == "ontoaligner kge" else None


