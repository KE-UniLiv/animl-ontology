import re
import pandas as pd
import os
from rdflib import Graph

def extract_label(entity_uri: str, content: str) -> str:
    """
    
    Extracts the label of an entity from the given content if no rdfs:label is present within the content of the entity.

    Parameters:
        entity_uri (str): The URI of the entity whose label is to be extracted.
        content (str): The content from which to extract the label.
    
    Returns:
        str: The extracted label if found, otherwise an empty string.
        If the entity has no label, it returns an empty string.
    
    
    
    """

    # Try to match <rdfs:label>...</rdfs:label>
    label_match = re.search(
        rf'<rdfs:label>(.*?)</rdfs:label>', content
    )
    if label_match:
        return label_match.group(1)
    # Try to match <AnnotationAssertion> with the entity and a Literal
    # Accept both full URI and QName (e.g., af-p:AFP_0001046)
    entity_id = entity_uri.split("/")[-1].split("#")[-1]
    ann_pattern = (
        rf'<AnnotationAssertion>\s*'
        rf'<AnnotationProperty[^>]*rdfs:label[^>]*/>\s*'
        rf'<AbbreviatedIRI>([^<]*{re.escape(entity_id)})</AbbreviatedIRI>\s*'
        rf'<Literal>(.*?)</Literal>'
    )
    ann_match = re.search(ann_pattern, content, re.DOTALL)
    if ann_match:
        return ann_match.group(2)
    return ""

def ensure_text_field(entity_list):
    """
    
    Simple aligner needs text field in the entity list to work properly.

    Arguments:
        entity_list: List of entities to ensure text field.

    Returns:
        List of entities with text field added if it was missing.

    """
    for entity in entity_list:
        if "text" not in entity:
            entity["text"] = entity.get("label", entity.get("name", entity.get("iri", "")))
    return entity_list

def insert_labels_for_classes(ontology_path, out_path=None) -> None:
    """
    
    Given an ontology, this function inserts labels for each class if no rdfs:label is present.

    Parameters:
        ontology_path (str): Path to the ontology file.
        out_path (str, optional): Path to save the modified ontology. If None, overwrites the original file.
    
    Returns:
        None: The function does not return anything, but it modifies the ontology file by adding labels.
    
    """

    with open(ontology_path, 'r') as file:
        content = file.read()

    allclasses = re.findall(r'(<owl:Class\s+rdf:about="([^"]+)">.*?</owl:Class>)', content, re.DOTALL)

    for block, uri in allclasses:
        # Check if rdfs:label is present
        if "<rdfs:label>" not in block:
            label = uri.split("/")[-1]
            # Insert label before closing tag
            new_block = block.replace(
                "</owl:Class>",
                f'    <rdfs:label>{label}</rdfs:label>\n</owl:Class>'
            )
            content = content.replace(block, new_block)

    # Write to output file (or overwrite original)
    out_path = out_path if out_path else ontology_path
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Labels inserted and saved to {out_path}")

def insert_labels_to_mappings(mappings_tsv, source_document, target_document, out_path) -> None:
    """
    Insert labels into a mappings TSV file based on source and target documents.

    Parameters:
        mappings_tsv (str): Path to the mappings TSV file.
        source_document (str): Path to the source ontology document.
        target_document (str): Path to the target ontology document.
        out_path (str): Path to save the modified mappings TSV file.

    Returns:
        None: The function does not return anything, but it modifies the mappings file by adding labels.
    
    """
    data_df = pd.read_csv(mappings_tsv, sep="\t")

    data_df["SrcLabel"] = ""
    data_df["TgtLabel"] = ""

    with open(source_document, 'r') as src_file:
        src_content = src_file.read()
    with open(target_document, 'r') as tgt_file:
        tgt_content = tgt_file.read()

    for index, row in data_df.iterrows():
        src = row["SrcEntity"]
        tgt = row["TgtEntity"]

        data_df.at[index, "SrcLabel"] = extract_label(src, src_content)
        data_df.at[index, "TgtLabel"] = extract_label(tgt, tgt_content)

    data_df.to_csv(out_path, sep="\t", index=False)



def rdf_to_owl(rdf_file: str) -> None:
    """
    
    Convert RDF file to OWL format using rdflib.

    Parameters:
        rdf_file (str): Path to the RDF file to be converted.
    
    Returns:
        None: The function does not return anything, but it serializes the RDF graph to an OWL file.

    """

    g = Graph()
    g.parse(rdf_file, format='xml')

    g.serialize("D:/GitHub/XAnIML/alignment/ontologies/TheMusicOntology/moowl.owl", format='xml')

def csv_to_tsv(csv_file: str, tsv_file: str) -> None:
    """
    
    Convert a CSV file to TSV format quickly.

    Parameters:
        csv_file (str): Path to the input CSV file.
        tsv_file (str): Path to save the output TSV file.
    
    Returns:
        None: The function does not return anything, but it writes the TSV file.

    """

    df = pd.read_csv(csv_file)
    df.to_csv(tsv_file, sep='\t', index=False)


    

    