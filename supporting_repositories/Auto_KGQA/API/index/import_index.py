import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from API.configs import *
#Import T-Box index
if INDEX_T_BOX == "WHOOSH":
    from API.index.whoosh_index import TBoxIndex
elif INDEX_T_BOX == "FAISS":
    from API.index.vector_distance_index import TBoxIndex
elif INDEX_T_BOX == "SPOTLIGHT":
    from API.index.spotlight import TBoxIndex

#Import A-Box index
if INDEX_A_BOX == "WHOOSH":
    from API.index.whoosh_index import ABoxIndex
elif INDEX_A_BOX == "FAISS":
    from API.index.vector_distance_index import ABoxIndex
elif INDEX_A_BOX == "SPOTLIGHT":
    from API.index.spotlight import ABoxIndex