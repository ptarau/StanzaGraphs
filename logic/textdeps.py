import csv

import networkx as nx
import stanza

from params import *
from visualizer import *


class TextWorker:
    """
    Stanza-based NLP processor and builds text graph  derived
    from dependency links usable donwstream for algorithmic and
    deep-learning based information retrieval tasks.
    It also export its data as Prolog term and relation files.
    """

    def __init__(self, lang='en'):
        self.out = PARAMS['OUTPUT_DIRECTORY']
        self.pics = PARAMS['PICS']
        ensure_path(self.out)
        ensure_path(self.pics)
        self.fact_list = None
        self.lang = lang

        if not exists_file(home_dir() + '/stanza_resources/' + lang):
            stanza.download(lang)

        self.nlp = stanza.Pipeline(lang=lang, logging_level='ERROR')

    # process text from a file
    def from_file(self, fname=None):
        self.fname = fname
        text = file2text(fname + ".txt")
        self.fact_list = None
        self.doc = self.nlp(text)

    # process text from a string
    def from_text(self, text="Hello!"):
        self.fname = 'from_text'
        self.fact_list = None
        self.doc = self.nlp(text)

    def get_text(self):
        return self.doc.text

    def facts(self):
        if self.fact_list is None:
            self.fact_list = list(self.generate_facts())
        return self.fact_list

    def generate_facts(self):
        """generates <from,from_tag,relation,to_tag,to,sentence_id> tuples"""

        def is_ascii(s):
            return all(ord(c) < 128 for c in s)

        def good_word(x):
            w = x.lemma
            tag = x.upos
            ok = tag[0] in "NVJ" or tag in {'ADJ', 'ADV', 'PROPN'}
            ok = ok and len(w) > 2 and w.isalnum() and is_ascii(w)
            return ok

        def fact(x, sent, sid):
            if not good_word(x): return None
            xid = x.id
            w = x.lemma
            tag = x.upos
            hw = sent.words[x.head - 1]
            h = hw.lemma
            if x.head == 0:
                return w, x.upos, 'PREDICATE_OF', 'SENT', sid, xid, sid
            else:
                # print('!!!', w, h)
                return w, tag, x.deprel, hw.upos, h, xid, sid

        sent_id = 0
        for sentence in self.doc.sentences:
            sent_id += 1

            for word in sentence.words:
                res = fact(word, sentence, sent_id)
                if res: yield res

    def to_nx_graph(self):  # converts to networkx graph
        g = facts2nx(self.facts())
        g = g.reverse()
        return g

    def to_nx_tree(self):
        """ converts to networkx graph """
        g = self.to_nx_graph()
        s = 'TEXT_ROOT'
        if s not in g.nodes: g.add_node(s)
        if not nx.is_directed_acyclic_graph(g):
            g = nx.dfs_tree(g, source=s)
        return g

    def to_tsv(self):  # writes out edges to .tsv file
        facts2tsv(self.facts(), self.out + self.fname + ".tsv")
        self.to_sents()

    def to_prolog(self):  # writes out edges to Prolog file
        facts2prolog(self.facts(), self.out + self.fname + ".pro")

    def get_sent(self, sid):
        return self.doc.sentences[sid].text

    # writes out sentences
    def to_sents(self):
        def sent_gen():
            for sid, sent in enumerate(self.doc.sentences):
                yield sid, sent.text

        facts2tsv(sent_gen(), self.out + self.fname + "_sents.tsv")

    def gshow(self, as_tree=True):
        if as_tree:
            tag = "tree"
            g = self.to_nx_tree()
        else:
            tag = "dag"
            g = self.to_nx_graph()
        print('NODES:', g.number_of_nodes(), 'EDGES:', g.number_of_edges())
        gshow(g, file_name=self.pics + self.fname + "_" + tag + ".gv")

    def as_term(self):
        g = self.to_nx_tree()

        def as_atomic(n):
            n = str(n)
            if n == 'TEXT_ROOT': n = 'text_term'
            if n and (n[0].isupper() or n[0] == '_' or n[0].isdigit()):
                n = "'" + n + "'"
            return n

        def from_root(n):
            h = as_atomic(n)
            if g.out_degree(n) == 0: return h
            ms = nx.neighbors(g, n)
            xs = [from_root(m) for m in ms]
            s = ",".join(xs)
            return "".join([h, "(", s, ")"])

        return from_root("TEXT_ROOT")


# read a file into a string text
def file2text(fname):
    with open(fname, 'r') as f:
        return f.read()


def facts2nx(fgen):
    """
    turns edges into networkx DiGraph
    edges also contain "root" links to
    sentence they originate from
    """
    g = nx.DiGraph()

    for f, ff, rel, tt, t, xid, sid in fgen:
        if f == t or (t, f) in g.edges: continue
        if rel == 'PREDICATE_OF': t = 'TEXT_ROOT'
        g.add_edge(f, t, rel=ff + "_" + rel + "_" + tt)

    # if not nx.is_directed_acyclic_graph(g):
    #    gshow(g,file_name="EXPECTED_DAG")
    return g


# writes out edge facts as .tsv file
def facts2tsv(fgen, fname):
    ensure_path(fname)
    with open(fname, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for fact in fgen:
            writer.writerow(fact)


# writes out edge facts as Prolog file
def facts2prolog(fgen, fname):
    ensure_path(fname)
    with open(fname, 'w') as f:
        for fact in fgen:
            print('edge', end='', file=f)
            print(fact, end=".\n", file=f)


def process_file(fname=None):
    nlp = TextWorker()
    nlp.from_file(fname)
    nlp.to_tsv()
    nlp.to_prolog()
    return nlp


def home_dir():
    from pathlib import Path
    return str(Path.home())


# TESTS


def test_merger():
    text = """
Logic Programming and Functional Programming are declarative programming paradigms. 
Evaluation in Logic Programs is eager while for functional programs it may be lazy. 
As a common feature, unification is used for evaluation in Logic Programming and 
for type inference in Functional Programming.
"""
    tm = TextWorker()
    text = text.lower()
    tm.from_text(text)
    g = tm.to_nx_tree()
    tm.to_prolog()
    # g = g.reverse(copy=False)
    tm.gshow(as_tree=True)
    #tm.gshow(as_tree=False)

    d = nx.pagerank(g)
    m = sorted(d.items(), reverse=True, key=lambda x: x[1])
    for w in m:
        print(w)

    print(tm.as_term())


if __name__ == "__main__":
    pass
    test_merger()
