
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

## -- DeepOnto imports --
from deeponto.onto import Ontology
from deeponto.align.bertmap import BERTMapPipeline, DEFAULT_CONFIG_FILE

## -- OntoAligner imports --
from ontoaligner.ontology import GraphTripleOMDataset, AniMLAllotropeOMDataset, FishZooplanktonOMDataset
from ontoaligner.utils import metrics, xmlify
from ontoaligner.aligner import TransDAligner, TransEAligner, DistMultAligner, ComplExAligner, RotatEAligner, CompGCNAligner, ConvEAligner, AutoModelDecoderLLM, ConceptLLMDataset, BM25Retrieval, TFIDFRetrieval, SVMBERTRetrieval, SBERTRetrieval, MistralLLMBERTRetrieverRAG, SimpleFuzzySMLightweight, WeightedFuzzySMLightweight, TokenSetFuzzySMLightweight
from ontoaligner.encoder import GraphTripleEncoder, ConceptLLMEncoder, ConceptParentRAGEncoder, ConceptParentLightweightEncoder
from ontoaligner.postprocess import graph_postprocessor, rag_hybrid_postprocessor, retriever_postprocessor, TFIDFLabelMapper, llm_postprocessor

## -- Miscellaneous imports --
from huggingface_hub import login
from utils import ensure_text_field
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from utils import get_key

import torch
import utils
import deeponto.align.logmap
import subprocess
import json
import wandb
import evaluation
