# based on https://www.sbert.net/index.html

import os
import pickle

import sentence_transformers as st
from textstar import *

# import pandas as pd


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
    lss=text2sents(text)

    sents=[ls[1] for ls in lss]

    enc=SequenceEncoder()

    print(sents[0])
    vects=enc(sents,'../out/cache.pickle')
    print(vects[0])


test_embeddings()
