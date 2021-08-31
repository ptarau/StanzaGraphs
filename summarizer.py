import csv
import math
from collections import defaultdict

import networkx as nx
import stanza

from params import *
from rankers import ranker_dict
from translator import translate
from visualizer import gshow


class Summarizer:
    """
    Stanza-based multi-lingual NLP processor
    that extracts summaries and keywords
    and builds text graph edge files derived
    from dependency links usable donwstream
    for algorithmic and deep-learning based
    information retrieval tasks
    """

    def __init__(self, lang=None):
        self.out = PARAMS['OUTPUT_DIRECTORY']
        ensure_path(self.out)
        ensure_path("pics/")
        self.set_language(lang=lang)
        self.fact_list = None

    def set_language(self, lang=None):
        self.lang = lang
        if lang is None: return

        if not exists_file(home_dir() + '/stanza_resources/' + lang):
            stanza.download(lang)

        self.nlp = stanza.Pipeline(lang=lang, logging_level='ERROR')

    def detect_language(self, text):
        detected = detect_lang(text)
        if self.lang is None or self.lang != detected:
            self.set_language(detected)

    # process text from a file
    def from_file(self, fname=None):
        self.fname = fname
        text = file2text(fname + ".txt")
        self.detect_language(text)
        self.fact_list=None
        self.doc = self.nlp(text)
        # print('LANGUAGE:',self.lang)

    def from_text(self, text="Hello!"):
        self.detect_language(text)
        self.fact_list = None
        self.doc = self.nlp(text)

    def is_keynoun(self, x):
        """true for "important" nouns"""
        ok = x.upos in ('NOUN', 'PROPN') and ('subj' in x.deprel or 'ob' in x.deprel)
        if self.lang == 'en': ok = ok and len(x.lemma) > 3
        return ok

    def get_text(self):
        return self.doc.text

    def cache_name(self):
        if not PARAMS['CACHING']: return None
        d = PARAMS['OUTPUT_DIRECTORY'] + 'CACHE/'
        f = d + self.fname + '_info_' + PARAMS['TARGET_LANG'] + '.json'
        ensure_path(f)
        return f

    def facts(self):
        if self.fact_list is None:
            self.fact_list = list(self.generate_facts())
        return self.fact_list

    def generate_facts(self):
        """generates <from,from_tag,relation,to_tag,to,sentence_id> tuples"""
        first_occ = dict()

        def fact(x, sent, sid):
            if x.head == 0:
                yield x.lemma, x.upos, 'PREDICATE_OF', 'SENT', sid, sid
            else:
                hw = sent.words[x.head - 1]
                if self.is_keynoun(x):  # reverse link to prioritize key nouns
                    yield hw.lemma, hw.upos, "rev_" + x.deprel, x.upos, x.lemma, sid
                    yield (sid, 'SENT', 'ABOUT', x.upos, x.lemma, sid)
                    if x.lemma not in first_occ:
                        first_occ[(x.lemma, x.upos)] = sid
                        yield (x.lemma, x.upos, 'DEFINED_IN', 'SENT', sid, sid)
                else:
                    yield x.lemma, x.upos, x.deprel, hw.upos, hw.lemma, sid
                if x.deprel in ("compound", "flat"):
                    comp = x.lemma + " " + hw.lemma
                    yield x.lemma, x.upos, 'IN', 'COMP', comp, sid
                    yield hw.lemma, hw.upos, 'IN', 'COMP', comp, sid
                    yield (sid, 'SENT', 'ABOUT', 'COMP', comp, sid)

        for sent_id, sentence in enumerate(self.doc.sentences):
            for word in sentence.words:
                yield from fact(word, sentence, sent_id)

    def keynouns(self):
        """collects important nouns"""
        ns = set()
        for sent in self.doc.sentences:
            for x in sent.words:
                if self.is_keynoun(x):
                    ns.add(x.lemma)
        return ns

    def context_dict(self):
        """
        returns contexts in which nouns and adjectives
        occur as constiguous lemmas as part of a phrase
        """
        contexts = defaultdict(list)
        for sid, sent in enumerate(self.doc.sentences):
            ws = list(sent.words)
            good = ('NOUN', 'ADJ')
            for i, w in enumerate(ws):
                if w.upos not in good: continue
                if i == 0 or i + 1 == len(ws): continue
                prev_w = ws[i - 1]
                next_w = ws[i + 1]
                context = [w.lemma]
                if prev_w.upos in good:
                    context = [prev_w.lemma] + context
                if next_w.upos in good:
                    context.append(next_w.lemma)
                if len(context) < 2: continue
                # phrase=" ".join(context)
                contexts[w.lemma].append((sid, context))
        return contexts

    def info(self):
        cname = self.cache_name()

        if cname and exists_file(cname):
            print('FROM CACHED: ', cname)
            sids, sents, kwds = from_json(cname)
            return kwds, sids, sents, None

        wk = PARAMS['k_count']
        sk = PARAMS['s_count']

        """extract keywords and summary sentences"""

        ranker = ranker_dict[PARAMS['RANKER']]
        g = self.to_nx()
        ranks = ranker(g)

        # print('@@@@@',ranks)

        def rank_phrase(pair):
            sid, ws = pair
            if sid not in ranks: return 0, ws
            r = sum(ranks[x] for x in ws if x in ranks)
            r = r * (ranks[sid] / (1 + math.log(1 + len(ws))))
            # r=ranks[sid]
            return (r, ws)

        def extend_kwd(w):
            cs = contexts[w]
            if not cs: return w
            rs = map(rank_phrase, cs)
            rs = sorted(rs, reverse=True, key=lambda x: x[0])
            phrase = " ".join(rs[0][1])
            return phrase

        ns = self.keynouns()
        contexts = self.context_dict()

        kwds, sids, picg = ranks2info(g, ranks, self.doc.sentences, ns, wk, sk, self.lang)
        kwds = map(extend_kwd, kwds)
        kwds = dict((k, 1) for k in kwds)  # remove duplicates, keep order
        kwds = [translate(w, source_lang=self.lang) for w in kwds]

        sids = sorted(sids)

        sents = map(self.get_sent, sids)
        sents = [translate(s, source_lang=self.lang) for s in sents]

        if cname:
            print('CACHING TO: ', cname)
            to_json((sids, sents, kwds), cname)

        if PARAMS['CACHING'] : self.to_tsv()
        return kwds, sids, sents, picg

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

    def summarize(self):  # extract summary and keywords
        kws, sids, sents, picg = self.info()
        print("\nSUMMARY:")
        for sid, sent in zip(sids, sents): print(sent, '-> [', sid, ']')
        print("\nKEYWORDS:")
        for w in kws: print(w, end='; ')
        print("\n")
        if picg: gshow(picg, file_name='pics/' + self.fname + '.gv')


# read a file into a string text
def file2text(fname):
    # with open(fname, 'r') as f:
    with open(fname, 'r', encoding="utf-8") as f:  # for process Vietnamese
        return f.read()


def facts2nx(fgen):
    """
    turns edges into networkx DiGraph
    edges also contain "root" links to
    sentence they originate from
    """
    d = defaultdict(list)
    g = nx.DiGraph()
    for f, ff, rel, tt, t, sid in fgen:
        d[(f, t)].append(sid)
    for (f, t), sids in d.items():
        w = 1 / len(sids)
        # ppp('WEIGHT:',f, '->',t,sids)
        g.add_edge(f, t, weight=w)
    return g


def good_sent(x, lang):
    if lang != 'en': return True
    if len(x) < 10: return False
    if not x[-1] in ".": return False
    if not x[0].isupper(): return False
    bad = sum(1 for _ in x if x.isdigit() or x in "@#$%^&*()[]{}-=+_;':<>/|~.")
    if bad > len(x) / 10:
        # print('!!!!', bad, x)
        return False
    return True


# uses rank dictionary to extract salient
# sentences and keywords
def ranks2info(g, ranks, sents, keyns, wk, sk, lang):
    ranked = sorted(ranks.items(), key=(lambda v: v[1]), reverse=True)
    sids = []
    kwds = []

    for x, r in ranked:
        if wk <= 0: break
        if isinstance(x, str) and x in keyns:
            kwds.append(x)
            wk -= 1
    for x, r in ranked:
        if sk <= 0: break
        if isinstance(x, int):
            text = sents[x].text
            if good_sent(text, lang):
                sids.append(x)
                sk -= 1

    # visualize
    if PARAMS['pics']:
        _, minr = ranked[(len(ranked) - 1) // 4]
        good = [x for (x, r) in ranked
                if isinstance(x, str)
                and "'" not in x
                and (r > minr or x in keyns)]
        picg = nx.DiGraph()
        for (x, y) in g.edges():
            if x in good and y in good:
                picg.add_edge(x, y)
    else:
        picg = None

    return kwds, sids, picg


# writes out edge facts as .tsv file
def facts2tsv(fgen, fname):
    ensure_path(fname)
    # with open(fname, 'w', newline='') as f:
    with open(fname, 'w', encoding="utf-8", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for fact in fgen:
            writer.writerow(fact)


# writes out edge facts as Prolog file
def facts2prolog(fgen, fname):
    ensure_path(fname)
    # with open(fname, 'w') as f:
    with open(fname, 'w', encoding="utf-8") as f:  # for process Vietnamese
        for fact in fgen:
            print('edge', end='', file=f)
            print(fact, end=".\n", file=f)


def process_file(fname=None):
    nlp = Summarizer()
    nlp.from_file(fname)
    nlp.to_tsv()
    return nlp


# TESTS

def test(fname='texts/english'):
    #nlp = Summarizer()
    #nlp.from_file(fname)
    nlp=process_file(fname=fname)
    nlp.summarize()


if __name__ == "__main__":
    # test(fname='texts/english')
    # test(fname='texts/cosmo')
    # test(fname='texts/spanish')
    # test(fname='texts/chinese')
    # test(fname='texts/russian')
    test(fname='texts/vietnamese')

