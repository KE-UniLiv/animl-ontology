"""

This script provides an implementation of various ontology alignment methods.
It includes functions to run different alignment techniques such as LogMap, BERTMap, lightweight alignments from ontoaligner, and KGE-based alignments from ontoaligner.

"""

from alignment_dependencies import *
from utils import insert_labels_for_classes

configpath = os.path.join(os.getcwd(), "alignment", "alignment_configs.yml")

wandb.login(key=get_key("wandb", config_file=configpath))
login(token=get_key("huggingface", config_file=configpath))

def get_ontologies() -> dict:
    """
    Get paths to the ontologies used in the alignment process.

    """

    ontologies = {
        "MusicMeta": os.path.join(os.getcwd(), "alignment", "ontologies", "MusicMeta", "musicmeta.owl"),
        "TheMusicOntology": os.path.join(os.getcwd(), "alignment", "ontologies", "TheMusicOntology", "moowl.owl"),
        "AniML": os.path.join(os.getcwd(), "alignment", "ontologies", "AniML", "animl.owl"),
        "Allotrope": os.path.join(os.getcwd(), "alignment", "ontologies", "AFO-2025_06", "afo", "voc", "afo", "merged", "REC", "2025", "06", "merged-without-qudt.xml"),
        "mouse-human-source": os.path.join(os.getcwd(), "alignment", "ontologies", "mouse-human", "source.xml"),
        "mouse-human-target": os.path.join(os.getcwd(), "alignment", "ontologies", "mouse-human", "target.xml"),
        "mouse-human-reference": os.path.join(os.getcwd(), "alignment", "ontologies", "mouse-human", "reference.xml"),
        "AniML Enriched": os.path.join(os.getcwd(), "alignment", "ontologies", "AniML", "animl_enriched.xml"),
        "fishref": os.path.join(os.getcwd(), "alignment", "ontologies", "fish-zooplankton", "reference.xml"),
        "FishS+": os.path.join(os.getcwd(), "alignment", "ontologies", "fish-zooplankton", "fish_zooplankton_source_enriched.xml"),
        "FishT+": os.path.join(os.getcwd(), "alignment", "ontologies", "fish-zooplankton", "fish_zooplankton_target_enriched.xml"),
        "FishS": os.path.join(os.getcwd(), "alignment", "ontologies", "fish-zooplankton", "source.xml"),
        "FishT": os.path.join(os.getcwd(), "alignment", "ontologies", "fish-zooplankton", "target.xml"),
    }

    return ontologies

# TODO, can parameterise
def run_logmap_direct(source_ontology, target_ontology, output_path) -> bool:
    """
    Run LogMap directly with an Ubuntu call 
    
    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.
        output_path (str): Path where the output mappings will be saved.

    Returns:
        bool: True if the process completed successfully, False otherwise.
    
    """
    
    # Find the LogMap jar file
    logmap_dir = os.path.dirname(deeponto.align.logmap.__file__)
    jar_path = os.path.join(logmap_dir, "logmap-matcher-4.0.jar")

    print(f"LogMap JAR path: {jar_path}")


    # Build the command for MATCHER mode (to create initial mappings)
    cmd = [
        "wsl", "java", "--add-opens", "java.base/java.lang=ALL-UNNAMED",
        "-Xms500m", "-Xmx10g", "-DentityExpansionLimit=100000000",
        "-jar", "/mnt/c/Users/ellio/AppData/Local/Programs/Python/Python313/Lib/site-packages/deeponto/align/logmap/logmap-matcher-4.0.jar",
        "MATCHER", 
        "file:///mnt/d/GitHub/animl-ontology/alignment/ontologies/AniML/animl.owl",
        "file:///mnt/d/GitHub/animl-ontology/alignment/ontologies/AFO-2025_06/afo/voc/afo/merged/REC/2025/06/merged-without-qudt.xml",
        "/mnt/d/GitHub/animl-ontology/alignment/outputs/logmap/logmap2_mappings.owl",
        "false"
    ]

    print("Running command:", " ".join(cmd))
    
    # Run the command with real-time output
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                              text=True, universal_newlines=True)
    
    # Print output in real-time
    for line in process.stdout:
        print(line.rstrip())
    
    # Wait for completion
    process.wait()
    
    return process.returncode == 0

def run_bertmap_direct(source_ontology_path: str, target_ontology_path: str) -> None:
    """
    Run BERTMap directly with the DeepOnto scripts

    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.

    Returns:
        None: The function does not return anything, but it initializes the BERTMapPipeline with the provided ontologies,
        and computes the mapping scores for class pairs.


    """
    
    # Create temporary copies of ontologies with labels added
    source_with_labels = source_ontology_path.replace('.owl', '_with_labels.owl')
    
    # Add labels to source ontology if it doesn't have them
    print(f"Adding labels to source ontology: {source_ontology_path}")
    insert_labels_for_classes(source_ontology_path, source_with_labels)
    
    # Add labels to target ontology if it doesn't have them
    #print(f"Adding labels to target ontology: {target_ontology_path}")
    #insert_labels_for_classes(target_ontology_path, target_with_labels)

    config = BERTMapPipeline.load_bertmap_config(DEFAULT_CONFIG_FILE)

    source = source_with_labels
    target = target_ontology_path

    ontolsource = Ontology(source)
    ontaltarget = Ontology(target)

    bertmap = BERTMapPipeline(ontolsource, ontaltarget, config)

    class_pairs_to_score = []

    for src_class_iri, tgt_class_iri in class_pairs_to_score:

        src_class_annotations = bertmap.src_annotation_index[src_class_iri]
        tgt_class_annotations = bertmap.tgt_annotation_index[tgt_class_iri]

        score = bertmap.mapping_predictor.bert_mapping_score(src_class_annotations, tgt_class_annotations)

        bertmaplt_score = bertmap.mapping_predictor.edit_similarity_mapping_score(src_class_annotations, tgt_class_annotations)

        with open(os.path.join(os.getcwd(), "bertmap", "class_pairs_scores.json"), "w") as f:
            json.dump({
                "source_class": src_class_iri,
                "target_class": tgt_class_iri,
                "score": score,
                "bertmaplt_score": bertmaplt_score
            }, f, indent=4)

def run_rag_large_ontoaligner(source_ontology: str, target_ontology: str, reference_ontology: str, output_path: str, task, 
                              encoder = ConceptParentRAGEncoder()) -> None:
    """
    
    Run heavyweight OA method with a given task.

    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.
        reference_ontology (str): Path to the reference ontology file.
        output_path (str): Path where the output mappings will be saved.
        task (Class): The task to collect the dataset.
    
    Returns:
        None: The function does not return anything, but it collects the dataset, runs the aligner,
        encodes the ontology, and writes the matchings to an XML file.
    
    """
    print(f"Task: {task}")

    dataset = task.collect(
        source_ontology_path=source_ontology,
        target_ontology_path=target_ontology,
        reference_matching_path=reference_ontology
    )

    encoded_ontology = encoder(source=dataset['source'], target=dataset['target'])

    retriever_config = {'device': 'cpu', "top_k": 5}
    llmconfig = {
    'device': 'cpu', 
    'max_length': 300, 
    "max_new_tokens": 10, 
    "batch_size": 15,
    'huggingface_access_token': "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",
    'token': "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",
    'use_auth_token': True
}

    model = MistralLLMBERTRetrieverRAG(retriever_config=retriever_config, llm_config=llmconfig)
    model.load(llm_path="mistralai/Mistral-7B-v0.3", ir_path="all_MiniLM-L6-v2")
    predictions = model.generate(input_data=encoded_ontology)

    hybrid_matchings, hybrid_configs = rag_hybrid_postprocessor(predicts=predictions, 
                                                                ir_score_threshold=0.1, 
                                                                llm_confidence_th=0.8)
    
    evaluation = metrics.evaluation_report(predicts=hybrid_matchings, references=dataset['reference']) ## -- Can be dumped into a json eval report

    xml_str = xmlify.xml_alignment_generator(matchings=hybrid_matchings)
    open(output_path, "w", encoding="utf-8").write(xml_str)

def run_lightweight_ontoaligner(source_ontology: str, target_ontology: str, output_path: str, typeof: str, 
                                threshold: float = 0.7, task=FishZooplanktonOMDataset()) -> None:
    """
    
    Run a lightweight OA method with a given threshold.

    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.
        reference (str): Path to the reference ontology file.
        output_path (str): Path where the output mappings will be saved.
        task (MouseHumanOMDataset): The task to collect the dataset.
        threshold (float): The threshold for the lightweight aligner.

    Returns:
        None: The function does not return anything, but it collects the dataset, runs the aligner,
        encodes the ontology, and writes the matchings to an XML file.
    
    """

    print(f"Task: {task}")

    dataset = task.collect(
        source_ontology_path=source_ontology,
        target_ontology_path=target_ontology
    )


    aligner = SimpleFuzzySMLightweight(threshold=threshold) if typeof == "Fuzzy" else \
              WeightedFuzzySMLightweight(threshold=threshold) if typeof == "WeightedFuzzy" else \
              TokenSetFuzzySMLightweight(threshold=threshold) if typeof == "TokenSetFuzzy" else None

    source_entities = ensure_text_field(dataset['source'])
    target_entities = ensure_text_field(dataset['target'])

    matchings = aligner.generate(input_data=(source_entities, target_entities))
    xml_str = xmlify.xml_alignment_generator(matchings=matchings)

    open(output_path, "w", encoding="utf-8").write(xml_str)

def run_retriever_ontoaligner(source_ontology: str, target_ontology: str, output_path: str, typeof: str, 
                              task=AniMLAllotropeOMDataset(), top_k: int = 5, encoder=ConceptParentLightweightEncoder()) -> None:
    """
    
    Run the retriever-based OA method with a given task to encode Ontology concepts into dense vectors

    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.
        output_path (str): Path where the output mappings will be saved.
        reference (str): Path to the reference ontology file.
        typeof (str): Type of the retriever alignment method to use (e.g., "SBERTRetrieval", "SVMBERTRetrieval", "TFIDFRetrieval").
        task (MouseHumanOMDataset): The task to collect the dataset.
        top_k (int): The number of top matches to retrieve.

    Returns:
        None: The function does not return anything, but it collects the dataset, runs the aligner,
        encodes the ontology, generates matchings, and writes them to an XML file.
    
    """
    
    dataset = task.collect(
        source_ontology_path=source_ontology,
        target_ontology_path=target_ontology
    )

    encoded_ontology = encoder(source=dataset['source'], target=dataset['target'])

    aligner = SBERTRetrieval(top_k=top_k) if typeof == "SBERTRetrieval" else \
              SVMBERTRetrieval(top_k=top_k) if typeof == "SVMBERTRetrieval" else \
              TFIDFRetrieval(top_k=top_k) if typeof == "TFIDFRetrieval" else \
              BM25Retrieval(top_k=top_k) if typeof == "BM25Retrieval" else None

    aligner.load(path="all-MiniLM-L6-v2")

    matchings = aligner.generate(input_data=encoded_ontology)
    matchings = retriever_postprocessor(matchings) 

    if dataset['reference']:
        evals = metrics.evaluation_report(predicts=matchings, references=dataset['reference'])
        json.dumps(evals, indent=4)

    xml_str = xmlify.xml_alignment_generator(matchings=matchings)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

def run_llm_ontoaligner(source_ontology: str, target_ontology: str, output_path: str, reference: str, task) -> None:
    """
    
    Runs the LLM-based OA method with a given task to encode Ontology concepts into dense vectors

    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.
        output_path (str): Path where the output mappings will be saved.
        reference (str): Path to the reference ontology file.
        task (class): The task to collect the dataset.
    
    Returns:
        None: The function does not return anything, but it collects the dataset, encodes the ontology,
        generates matchings using an LLM, and writes them to an XML file.

    
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    dataset = task.collect(
        source_ontology_path=source_ontology,
        target_ontology_path=target_ontology,
        reference_matching_path=reference
    )
    
    encoder = ConceptLLMEncoder()

    source, target = encoder(source=dataset['source'], target=dataset['target'])
    llm_dataset = ConceptLLMDataset(source_onto=source, target_onto=target)

    dataloader_llm = DataLoader(llm_dataset, batch_size=2048, shuffle=False, collate_fn=llm_dataset.collate_fn)

    model = AutoModelDecoderLLM(device=device, max_length=300, max_new_tokens=10)
    model.load(path="mpt")

    predictions = []
    for batch in tqdm(dataloader_llm):
        prompts = batch["prompts"]
        sequences = model.generate(prompts)
        predictions.extend(sequences)
    
    mapper = TFIDFLabelMapper(classifier=LogisticRegression(), ngram_range=(1, 1))
    matchings = llm_postprocessor(predicts=predictions, mapper=mapper, dataset=llm_dataset)

    xml_str = xmlify.xml_alignment_generator(matchings=matchings)
    with open(output_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(xml_str)

def run_kge_ontoaligner(source_ontology: str, target_ontology: str, output_path: str, 
                        task=GraphTripleOMDataset(), method: str = "ConvE", referencepath=None) -> None:
    
    """
    
    Runs the knowledge graph embedding (KGE) based OA method with a given task to encode Ontology concepts into dense vectors.

    Options for the aligner method is given in the questionary prompt

    Parameters:
        source_ontology (str): Path to the source ontology file.
        target_ontology (str): Path to the target ontology file.
        output_path (str): Path where the output mappings will be saved.
        task (GraphTripleOMDataset): The task to collect the dataset.
        method (str): The KGE method to use for alignment (e.g., "ConvE", "TransD", "TransE", "DistMult", "ComplEx", "RotatE", "CompGCN"). Defaults to "ConvE".)

    Returns:
        None: The function does not return anything, but it collects the dataset, encodes the ontology,
        generates matchings using the specified KGE method, and writes them to an XML file.
    
    """


    # TODO parameterise
    task.ontology_name="animl-allotrope"

    dataset = task.collect(
        source_ontology_path=source_ontology,
        target_ontology_path=target_ontology,
        reference_matching_path=referencepath
    )
    
    encoder = GraphTripleEncoder()
    encoded_dataset = encoder(**dataset)

    kge_parameters = {
        'device': 'cpu',
        'embedding_dim': 300,
        'num_epochs': 30,
        'train_batch_size': 128,
        'eval_batch_size': 64,
        'num_negs_per_pos': 5,
        'random_seed': 42,
    }

    aligner = ConvEAligner(**kge_parameters) if method == "ConvE" else \
              TransEAligner(**kge_parameters) if method == "TransE" else \
              DistMultAligner(**kge_parameters) if method == "DistMult" else \
              ComplExAligner(**kge_parameters) if method == "ComplEx" else \
              RotatEAligner(**kge_parameters) if method == "RotatE" else \
              TransDAligner(**kge_parameters) if method == "TransD" else \
              CompGCNAligner(**kge_parameters) if method == "CompGCN" else None
    
    reverse_ontologies = {v: k for k, v in get_ontologies().items()}
    matchings = aligner.generate(input_data=encoded_dataset)

    processed = graph_postprocessor(predicts=matchings, threshold=0.5)   

    evaluation.compute_evaluation(predicts_pre=matchings, predicts_post=processed, 
                                         reference=dataset['reference'], 
                                         filepath=os.path.dirname(output_path),
                                         type=method, 
                                         source=reverse_ontologies.get(source_ontology), 
                                         target=reverse_ontologies.get(target_ontology))



    xml_str = xmlify.xml_alignment_generator(matchings=processed)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)


def insert_labels(ontology_path: str) -> None:
    """
    
    Calls the utility function to insert label tags for owl:Class entities

    Parameters:
        ontology_path (str): Path to the ontology file where labels will be inserted.
    
    Returns:
        None: The function does not return anything, but it modifies the ontology file by inserting labels for classes.
    
    """
    utils.insert_labels_for_classes(ontology_path)


if __name__ == '__main__':
    print("Without error")

