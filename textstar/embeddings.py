# based on https://www.sbert.net/index.html

import os
import pickle
#import networkx as nx

import sentence_transformers as st
from sklearn.neighbors import NearestNeighbors
import pygraphviz as pg

from textstar import *


def exists_file(fname):
    """tests  if it exists as file or dir """
    return os.path.exists(fname)


def ensure_path(fname):
    """
    makes sure path to directory and directory exist
    """
    d, _ = os.path.split(fname)
    os.makedirs(d, exist_ok=True)


def to_pickle(obj, fname):
    """
    serializes an object to a .pickle file
    """
    ensure_path(fname)
    with open(fname, "wb") as outf:
        pickle.dump(obj, outf)


def from_pickle(fname):
    """
    deserializes an object from a pickle file
    """
    with open(fname, "rb") as inf:
        return pickle.load(inf)


class SequenceEncoder():
    def __init__(self, model_name='all-MiniLM-L6-v2', device='cpu'):
        self.device = device
        self.model = st.SentenceTransformer(model_name, device=device)

    def __call__(self, values, cache):
        if exists_file(cache):
            x = from_pickle(cache)
            return x

        x = self.model.encode(values, show_progress_bar=True,
                              convert_to_tensor=False, device=self.device)
        to_pickle(x, cache)
        return x


def test_embeddings(fname='../texts/english'):
    with open(fname + ".txt", 'r') as f:
        text = f.read()
    lss = text2sents(text)

    sents = [ls[1] for ls in lss]

    enc = SequenceEncoder()

    print(sents[0])
    vects = enc(sents, 'out/cache.pickle')

    nbrs = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(vects)
    distances, indices = nbrs.kneighbors(vects)
    m = nbrs.kneighbors_graph(vects, n_neighbors=3, mode="distance")

    print(distances, '\n', indices)

    g = nx.from_scipy_sparse_matrix(m)
    for n,s in enumerate(sents):
        print(n,s)
        g.nodes[n]['sent']=s

    print(g.number_of_edges())

    a=nx.nx_agraph.to_agraph(g)
    a.draw("emb.pdf",prog='dot')

    d=nx.to_dict_of_dicts(g)
    print(d)



test_embeddings()
