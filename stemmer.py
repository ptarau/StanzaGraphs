from collections import defaultdict, Counter

import nltk

from params import *


class Stemmer:
    def __init__(self):
        self.stemmer = nltk.stem.SnowballStemmer('english')
        self.stops = self.get_stops()
        # symbol table
        self.w2i = dict()
        self.i2w = []
        self.ctr = Counter()
        self.all_sids = []
        self.maxlen = 0
        self.minlen = 1 << 16
        self.occs = defaultdict(list)
        self.too_short = 1

    def stem(self, w):
        return self.stemmer.stem(w)

    def sym(self, w):
        i = self.w2i.get(w, None)
        if i is None:
            i = len(self.i2w)
            self.i2w.append(w)
            self.w2i[w] = i
        return i

    def at(self, i):
        # if i >= 0 and i < len(self.i2w):
        return self.i2w[i]
        # return None

    def get_stops(self):
        with open("stopwords.txt", 'rt') as f:
            text = f.read()
            return text.split('\n')

    def to_syms(self, text):
        syms = set()
        sent_text = nltk.sent_tokenize(text)
        for sentence in sent_text:
            tokenized_text = nltk.word_tokenize(sentence)
            wts = nltk.pos_tag(tokenized_text)
            for w, t in wts:
                if t[0] in "NVJ" and w not in self.stops:
                    w = self.stem(w)
                    if len(w) < 4: continue
                    syms.add(w)
        return syms

    def syms_of(self, g):
        for n in g.nodes():
            title = g.nodes[n]['title']
            abstr = g.nodes[n]['abstr']
            text = title + ". " + abstr
            syms = self.to_syms(text)

            for w in syms:
                self.ctr[w] += 1

            yield n, syms  # node+syms in it

            if n % 100 == 0: print(n)
            # if n > 5: break

    def trim_syms(self, all_syms):
        self.ctr = dict((x, k) for (x, k) in self.ctr.most_common() if k > self.too_short)
        xss = []
        for n, syms in all_syms:
            xs = set(w for w in syms if w in self.ctr)
            xss.append((n, sorted(xs)))
        symlist = set(s for _, syms in xss for s in syms)

        for n, syms in xss:
            sids = set()
            for w in syms:
                if w in self.ctr:
                    i = self.sym(w)
                    self.occs[i].append(n)
                    sids.add(i)
            sids = sorted(sids)
            self.maxlen = max(self.maxlen, len(sids))
            self.minlen = min(self.minlen, len(sids))
            self.all_sids.append(sids)
        # pp(self.occs.items())

    def run(self, fname='experiments/arxiv.pickle'):
        ensure_path('experiments/out/no_such_file')
        g = from_pickle(fname)
        all_syms = list(self.syms_of(g))
        self.trim_syms(all_syms)

        with open('experiments/out/stems.tsv', 'wt') as wf:
            for sids in self.all_sids:
                sids = sorted(sids)
                sids = map(str, sids)
                line = "\t".join(sids)
                print(line, file=wf)

        with open('experiments/out/scounts.tsv', 'wt') as cf:

            for i, ks in self.occs.items():
                # ks = sorted(ks)
                items = [self.at(i), str(i), str(len(ks))]
                print("\t".join(items), file=cf)

            to_json(self.occs, 'experiments/out/swhere.json')
        print('MAX_MIN', self.maxlen, self.minlen)


if __name__ == "__main__":
    S = Stemmer()
    S.run()
