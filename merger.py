import os
import csv

import networkx as nx
import stanza

#from params import *
from visualizer import *


class TreeMerger:
    """
    Stanza-based multi-lingual NLP processor
    that extracts summaries and keywords
    and builds text graph edge files derived
    from dependency links usable donwstream
    for algorithmic and deep-learning based
    information retrieval tasks
    """

    def __init__(self, lang='en'):
        self.out = 'out/' # PARAMS['OUTPUT_DIRECTORY']
        ensure_path(self.out)
        ensure_path("pics/")
        self.fact_list = None
        self.lang = lang

        if not exists_file(home_dir() + '/stanza_resources/' + lang):
            stanza.download(lang)

        self.nlp = stanza.Pipeline(lang=lang, logging_level='ERROR')
        self.stops = set(self.get_stops())

    # process text from a file
    def from_file(self, fname=None):
        self.fname = fname
        text = file2text(fname + ".txt")
        self.fact_list = None
        self.doc = self.nlp(text)

    def from_text(self, text="Hello!"):
        self.fname='from_text'
        self.fact_list = None
        self.doc = self.nlp(text)

    def is_keynoun(self, x):
        """true for "important" nouns"""
        ok = x.upos in ('NOUN', 'PROPN') and ('subj' in x.deprel or 'ob' in x.deprel)
        if self.lang == 'en': ok = ok and len(x.lemma) > 3
        return ok

    def get_text(self):
        return self.doc.text

    def get_stops(self):
        with open("stopwords.txt", 'rt') as f:
            text = f.read()
            return text.split('\n')

    def facts(self):
        if self.fact_list is None:
            self.fact_list = list(self.generate_facts())
        return self.fact_list

    def generate_facts(self):
        """generates <from,from_tag,relation,to_tag,to,sentence_id> tuples"""

        def fact(x, sent, sid):
            xid = x.id
            w = x.lemma
            tag = x.upos
            hw = sent.words[x.head - 1]
            h = hw.lemma
            if x.head == 0:
                return w, x.upos, 'PREDICATE_OF', 'SENT', sid, xid, sid
            elif tag[0] not in "NVJ" and tag not in {'ADJ', 'ADV', 'PROPN'}:
                # print('TAG:',w,tag)
                return None
            # elif w in self.stops: return None
            elif len(w) < 2 or w == h:
                return None
            else:
                # print('!!!', w, h)
                return w, tag, x.deprel, hw.upos, h, xid, sid

        sent_id = 0
        for sentence in self.doc.sentences:
            sent_id += 1

            for word in sentence.words:
                res = fact(word, sentence, sent_id)
                if res: yield res

    def to_nx(self):  # converts to networkx graph
        return facts2nx(self.facts())

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
        if (t, f) in g.edges: continue
        if rel == 'PREDICATE_OF':
            t = 'TEXT_ROOT'
        g.add_edge(f, t, rel=ff + "_" + rel + "_" + tt)
    return g


def midrank(g):
    d=nx.pagerank(g)
    rg=g.reverse(copy=False)
    rd=nx.pagerank(rg)
    m=dict()
    for (w,r) in d.items():
        m[w]=(r+rd[w])/2
    return m

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
    nlp = TreeMerger()
    nlp.from_file(fname)
    nlp.to_tsv()
    nlp.to_prolog()
    return nlp


def ensure_path(fname):
    folder, _ = os.path.split(fname)
    os.makedirs(folder, exist_ok=True)

def exists_file(fname):
    """ if it exists as file or dir"""
    return os.path.exists(fname)


def home_dir():
    from pathlib import Path
    return str(Path.home())


# TESTS


def large():
    tm = TreeMerger()
    tm.from_file('texts/cosmo')
    g = tm.to_nx()
    print(g.number_of_nodes())
    tm.to_prolog()
    gshow(g)  # .reverse(copy=False))

def medium():
    tm = TreeMerger()
    tm.from_file('texts/english')
    g = tm.to_nx()
    print(g.number_of_nodes())
    tm.to_prolog()
    gshow(g.reverse(copy=False))
    m = midrank(g)
    m = sorted(m.items(), reverse=True, key=lambda x: x[1])
    for w in m:
        print(w)


def small():
    text = """
    Penrose found that the dimensions of space and time switch roles inside a trapped surface. Time is the direction pointing toward the center, so that escaping a black hole is as impossible as going back in time. Penrose, together with Stephen Hawking, soon showed that a similar analysis applies to the entire universe: A singularity would have inevitably existed when matter and energy were densely packed together in the Big Bang.
    Penrose showed that, as he put it in his 1965 paper,  deviations from spherical symmetry cannot prevent space-time singularities from arising.  In other words, even when a star is distorted, it will still collapse down to a point. He showed this by introducing the notion of a trapped surface, as well as a now-famous diagrammatic scheme for analyzing how the surface sits inside space-time. Unlike a regular surface, which can have light rays shooting away from it in any direction, a trapped surface is a closed two-dimensional surface that — even when distorted so it’s no longer a sphere — only allows light rays to go one way: toward the center point.
     """

    tm = TreeMerger()
    tm.from_text(text)
    g = tm.to_nx()
    print(g.number_of_nodes())
    tm.to_prolog()
    g=g.reverse(copy=False)
    gshow(g)
    d=nx.pagerank(g)

    m=midrank(g)
    m = sorted(m.items(), reverse=True, key=lambda x: x[1])
    for w in m:
        print(w)


if __name__ == "__main__":
    #medium()
    small()
