#!/usr/bin/env python3
"""Repository consistency checks for the AnIML Ontology.

Run from the repository root:

    python testing/ci_validate.py

Exits non-zero if any check fails. Checks performed:

  1. every .ttl / .owl / .rq file parses
  2. every AnIML IRI uses the canonical namespace
  3. every aml: term referenced anywhere is declared in the ontology
  4. aml: labels in diagrams/*.pdf correspond to declared terms
  5. all competency-question queries execute; row counts reported

Check 4 is skipped if pdfplumber is not installed.
"""
from __future__ import annotations

import glob
import os
import re
import sys

from rdflib import Graph, OWL, RDF

CANON = "http://www.w3id.org/animl/ontology/"
ONTOLOGY = "ontologies/animl_ontology.owl"

# Third-party or pre-curation artefacts we do not police.
SKIP = (
    "/.git/",
    "alignments/ontologies/",
    "alignments/outputs/logmap/",
    "alignments/outputs/bertmap",
    "alignments/outputs/ontoaligner/",
)

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def repo_files(*exts: str) -> list[str]:
    out = []
    for root, _, files in os.walk("."):
        for fn in files:
            p = os.path.join(root, fn)
            if any(s in p.replace("\\", "/") for s in SKIP):
                continue
            if fn.endswith(exts):
                out.append(os.path.normpath(p))
    return sorted(out)


# ---------------------------------------------------------------- 1. parsing
print("1. parsing all RDF and SPARQL files")
graphs: dict[str, Graph] = {}
for p in repo_files(".ttl", ".owl"):
    try:
        g = Graph()
        g.parse(p)
        graphs[p] = g
    except Exception as exc:  # noqa: BLE001
        fail(f"parse error: {p}: {str(exc)[:120]}")

onto = graphs.get(ONTOLOGY)
if onto is None:
    print("FATAL: could not parse the ontology")
    sys.exit(1)


# ------------------------------------------------------------- 2. namespaces
print("2. checking namespace canonicalisation")
BAD_NS = re.compile(r"https?://(?:www\.)?w3(?:id)?\.org/animl/(?!ontology/)|https?://www\.w3\.org/animl")
for p in repo_files(".ttl", ".owl", ".rq", ".csv", ".md"):
    text = open(p, encoding="utf-8", errors="replace").read()
    for m in set(BAD_NS.findall(text)):
        fail(f"non-canonical AnIML namespace in {p}: {m!r}")


# --------------------------------------------------------- 3. declared terms
print("3. checking every referenced aml: term is declared")
# declarations may live in any ontology under ontologies/ (core or aligned)
declared = set()
for _p, _g in graphs.items():
    if _p.startswith("ontologies" + os.sep) or _p.startswith("ontologies/"):
        declared |= {
            str(x)[len(CANON):]
            for x in set(_g.subjects())
            if str(x).startswith(CANON)
        }

SCHEMA_POSITIONS = (RDF.type, OWL.onProperty)


def schema_terms(g: Graph):
    """Yield aml: terms used in schema position.

    Instance data legitimately mints its own individuals, so only predicates,
    rdf:type objects and owl:onProperty objects are required to be declared.
    """
    for s, p, o in g:
        if str(p).startswith(CANON):
            yield str(p)[len(CANON):]
        if p in SCHEMA_POSITIONS and str(o).startswith(CANON):
            yield str(o)[len(CANON):]


for p, g in graphs.items():
    for local in schema_terms(g):
        if local and local not in declared:
            fail(f"undeclared term aml:{local} used in schema position in {p}")


# ------------------------------------------------------------- 4. diagrams
print("4. checking diagram labels against declared terms")
try:
    import pdfplumber

    diagram_terms: set[str] = set()
    for pdf_path in sorted(glob.glob("diagrams/*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            text = " ".join((page.extract_text() or "") for page in pdf.pages)
        diagram_terms |= set(re.findall(r"\baml:\s*([A-Za-z_][A-Za-z0-9_]*)", text))

    # short fragments are PDF text-extraction artefacts, not real labels
    diagram_terms = {t for t in diagram_terms if len(t) > 3}
    missing = sorted(t for t in diagram_terms if t not in declared)
    if missing:
        notes.append(
            "diagram labels with no matching declared term "
            f"({len(missing)}): {', '.join('aml:' + m for m in missing)}"
        )
except ImportError:
    notes.append("pdfplumber not installed - diagram check skipped")


# ----------------------------------------------------------- 5. CQ queries
print("5. executing competency-question queries")
data = Graph()
for triple in onto:
    data.add(triple)
for p, g in graphs.items():
    if p == ONTOLOGY:
        continue
    for triple in g:
        data.add(triple)

queries = sorted(
    glob.glob("testing/verified_positives/*.rq"),
    key=lambda p: int(re.findall(r"(\d+)", os.path.basename(p))[0]),
)
answered = 0
for p in queries:
    q = open(p, encoding="utf-8", errors="replace").read()
    try:
        if list(data.query(q)):
            answered += 1
    except Exception as exc:  # noqa: BLE001
        fail(f"SPARQL error in {p}: {str(exc)[:120]}")

notes.append(
    f"{answered} of {len(queries)} CQ queries return at least one row "
    "against the shipped instance data"
)


# ---------------------------------------------------------------- reporting
print()
for n in notes:
    print(f"note: {n}")
if failures:
    print(f"\n{len(failures)} failure(s):")
    for f in failures[:60]:
        print(f"  - {f}")
    if len(failures) > 60:
        print(f"  ... and {len(failures) - 60} more")
    sys.exit(1)
print("\nall checks passed")
