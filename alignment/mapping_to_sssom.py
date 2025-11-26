import pandas as pd
import xml.etree.ElementTree as ET
import os
from glob import glob

def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
          "align": "http://knowledgeweb.semanticweb.org/heterogeneity/alignment"}

    rows = []
    for cell in root.findall(".//align:Cell", ns):
        e1 = cell.find("align:entity1", ns)
        e2 = cell.find("align:entity2", ns)
        rel = cell.find("align:relation", ns)
        measure = cell.find("align:measure", ns)

        if e1 is None or e2 is None or rel is None:
            continue

        rows.append({
            "subject_id": e1.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"),
            "predicate_id": "skos:exactMatch" if (rel.text or "").strip() == "=" else "skos:relatedMatch",
            "object_id": e2.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"),
            "confidence": float(measure.text) if measure is not None and measure.text else "",
            "mapping_justification": "semapv:AutomatedMapping",
            "creator_id": os.path.basename(xml_path),
            "source": os.path.basename(xml_path)
        })
    return rows

def convert_folder(xml_folder, output_path):
    all_rows = []
    for xml_file in glob(os.path.join(xml_folder, "*.xml")):
        all_rows.extend(parse_xml(xml_file))
    if not all_rows:
        print("No mappings found")
        return
    df = pd.DataFrame(all_rows)

    # Ensure SSSOM recommended columns and order (you can add more if needed)
    cols = ["subject_id", "predicate_id", "object_id", "confidence",
            "mapping_justification", "creator_id", "source"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""

    df = df[cols]

    # Write TSV directly (this produces a valid SSSOM-style TSV)
    df.to_csv(output_path, sep="\t", index=False, encoding="utf-8")
    print(f"Wrote {len(df)} mappings to {output_path}")

if __name__ == "__main__":
    convert_folder("alignment/outputs/ontoaligner/", "alignment/outputs/ontoaligner/all_mappings.sssom.tsv")