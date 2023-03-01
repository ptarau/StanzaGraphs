import csv
import math
from collections import defaultdict, Counter

import numpy as np
from sklearn.preprocessing import OneHotEncoder

from params import *
from summarizer import process_file, Summarizer, file2text
from translator import translate


# turns .tsv file into list of lists
def tsv2mat(fname):
    with open(fname) as f:
        wss = csv.reader(f, delimiter='\t')
        return list(wss)


class Data:
    """
    builds dataset from dependency edges in .tsv file associating
    <from,link,to> edges and sentences in which they occur;
    links are of the form POS_deprel_POS with POS and deprel
    tags concatenated
    """

    def __init__(self, fname=None):
        edge_file = PARAMS['OUTPUT_DIRECTORY'] + fname + ".tsv"
        if not exists_file(edge_file):
            nlp = process_file(fname=fname)
            self.lang = nlp.lang
        else:
            # print('!!! DETECT LANGUAGE',fname)
            self.lang = detect_lang(file2text(fname + ".txt"))

        wss = tsv2mat(edge_file)

        self.sents = tsv2mat(PARAMS['OUTPUT_DIRECTORY'] + fname + "_sents.tsv")
        occs = defaultdict(set)
        sids = set()
        lens = []
        for f, ff, r, tt, t, sid in wss:
            sid = int(sid)
            if len(lens) <= sid: lens.append(0)
            lens[sid] += 1
            # occs[(f, ff, r, tt, t)].add(sid)
            occs[(f, t)].add(sid)
            sids.add(sid)
        self.occs = occs  # dict where edges occur
        self.lens = lens  # number of edges in each sentence

        X, Y = list(zip(*list(occs.items())))
        X = np.array(X)
        y0 = np.array(sorted([x] for x in sids))

        # make OneHot encoders for X and y
        enc_X = OneHotEncoder(handle_unknown='ignore')
        enc_y = OneHotEncoder(handle_unknown='ignore')
        enc_X.fit(X)
        enc_y.fit(y0)
        hot_X = enc_X.transform(X).toarray()
        self.enc_X = enc_X
        self.enc_y = enc_y
        self.X = X
        # encode y as logical_or of sentence encodings it occurs in
        ms = []
        for ys in Y:
            m = np.array([[0]], dtype=np.float32)
            for v in ys:
                m0 = enc_y.transform(np.array([[v]])).toarray()
                m = np.logical_or(m, m0)
                m = np.array(np.logical_or(m, m0), dtype=np.float32)
            ms.append(m[0])
        hot_y = np.array(ms)

        self.hot_X = hot_X
        self.hot_y = hot_y

        print('\nFINAL DTATA SHAPES', 'X', hot_X.shape, 'y', hot_y.shape)
        # print('SENTENCE LENGTHS',lens)


class Query(Data):
    """
    builds <from,link,to> dependency links form a given
    text query and matches it against data to retrive
    sentences in which most of those edges occur
    """

    def __init__(self, fname=None):
        super().__init__(fname=fname)
        self.nlp_engine = Summarizer()


    def get_answers(self, text=None, k=3):
        """
        compute a similarity between
        set of edges in query and each sentence,
        then select the most similar ones
        """

        text = translate(text, target_lang=self.lang)

        #self.nlp_engine.fact_list = None
        self.nlp_engine.from_text(text)

        sids = []

        for f, ff, r, tt, t, _ in self.nlp_engine.facts():
            # sids.extend(self.occs.get((f, ff, r, tt, t), []))
            sids.extend(self.occs.get((f, t), []))

        c = Counter(sids)
        qlen = len(self.nlp_engine.facts())

        for sid in c:
            shared = c[sid]
            union_size = self.lens[sid] + qlen - shared
            # jaccard=shared/union_size
            # c[sid]=jaccard
            c[sid] = shared / math.log(union_size)

            # print('\nHIT WEIGHTS:', c, "\n")

        best = c.most_common(k)
        best = sorted(best)
        for sid, _ in best:
            sid, sent = self.sents[sid]
            sent = translate(sent, source_lang=self.lang)
            yield sid, sent

    def ask(self, text=None, interactive=False):
        """
        interacts if needed to collect query results
        """
        if not text:
            text = input("Query:")
        elif not interactive:
            print("Query:", text)

        answers = [sent for (_, sent) in self.get_answers(text=text)]
        self.print_answers(answers)

    def print_answers(self, answers):
        print('')
        for sent in answers:
            print(sent)
        print('')

    def show_answers(self, sids):
        print('')
        for sid in sids:
            sid, sent = self.sents[sid]
            sent = translate(sent, source_lang=self.lang)
            print(sent)
        print('')

    def interact(self):
        while True:
            text = input("Query: ")
            if not text: return
            self.ask(text=text, interactive=True)


# TESTS

def qtest():
    q = Query(fname='texts/english')
    q.ask(text="What did Penrose show?")
    q.ask(text="What was in Roger's 1965 paper?")


def dtest():
    d = Data(fname='texts/english')
    print("X", d.hot_X.shape)
    print(d.hot_X)
    print("y", d.hot_y.shape)
    print(d.hot_y)


def en_test():
    """ tests symbolic and neural QA on given document """
    i = Query(fname='texts/english')
    print("\n")
    print("ALGORITHMICALLY DERIVED ANSWERS:\n")
    i.ask("What did Penrose show about black holes?")
    i.ask(text="What was in Roger's 1965 paper?")
    print("\n")


def sp_test():
    """ tests symbolic and neural QA on given document """
    i = Query(fname='texts/spanish')
    print("\n")
    print("ANSWER(S) TO QUESTION ABOUT SPANISH TEXT:\n")
    i.ask("Who will face a debate this Tuesday?")
    i.ask("Who asked to wait for the winner of the election?")
    print("\n")


if __name__ == "__main__":
    en_test()
    #sp_test()
