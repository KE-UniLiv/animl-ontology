from ontoaligner.ontology import FishZooplanktonOMDataset, NellDbpediaOMDataset, HpMpOMDataset
from ontoaligner.utils import metrics, xmlify

import os
import json




def compute_evaluation(predicts_pre, predicts_post, reference, filepath, type, source, target):
    """    Compute evaluation metrics for the given predictions and reference alignment."""
    evals = metrics.evaluation_report(predicts=predicts_pre, references=reference)
    evals_post_processed = metrics.evaluation_report(predicts=predicts_post, references=reference)

    with open(filepath + f"{type}_{source}_2_{target}_preprocessed.json", "w") as f:
        json.dump(evals, f, indent=4)

    with open(filepath + f"{type}_{source}_2_{target}_postprocessed.json", "w") as f:
        json.dump(evals_post_processed, f, indent=4)