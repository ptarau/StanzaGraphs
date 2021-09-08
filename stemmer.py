from collections import defaultdict

import nltk

from params import *


class Stemmer:
    def __init__(self):
        self.stemmer = nltk.stem.SnowballStemmer('english')
        self.stops = self.get_stops()
        # symbol table
        self.w2i = dict()
        self.i2w = []
        self.sym(' ')  # will use to pad vectors to equal length
        self.maxlen = 0
        self.minlen = 1 << 16
        self.occs = defaultdict(set)
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
        if i >= 0 and i < len(self.i2w):
            return self.i2w[i]
        return None

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
                    i = self.sym(w)
                    # print(w, t, i)
                    syms.add(i)
        return syms

    def get_stops(self):
        with open("stopwords.txt", 'rt') as f:
            text = f.read()
            return text.split('\n')

    def syms_of(self, g):
        for n in g.nodes():
            title = g.nodes[n]['title']
            abstr = g.nodes[n]['abstr']
            text = title + ". " + abstr
            syms = self.to_syms(text)
            slen = len(syms)

            self.maxlen = max(self.maxlen, slen)
            self.minlen = min(self.minlen, slen)

            # if slen < 20: print('!!!', text, list(map(self.at, syms)))

            for w in syms:
                self.occs[w].add(n)

            if n % 1000 == 0: print(n)
            #if n > 200: break

            yield syms

    def run(self, fname='experiments/arxiv.pickle'):
        ensure_path('experiments/out/no_such_file')
        g = from_pickle(fname)
        all_syms = list(self.syms_of(g))

        shorts = set(i for i, ps in self.occs.items() if len(ps) <= self.too_short)

        with open('experiments/out/stems.tsv', 'wt') as wf:
            for syms in all_syms:
                shorties = syms & shorts
                for i in shorties:
                    syms.remove(i)
                    self.occs.pop(i)

                syms = sorted(syms)
                stems = map(str, syms)
                line = "\t".join(stems)
                print(line, file=wf)

        with open('experiments/out/scounts.tsv', 'wt') as cf:
            wks = []
            counts = sorted(self.occs.items(), reverse=True, key=lambda x: len(x[1]))
            for i, ks in counts:
                wks.append((i, sorted(list(ks))))
                items = [self.at(i), str(i), str(len(ks))]
                print("\t".join(items), file=cf)

            to_json(wks, 'experiments/out/swhere.json')
        print('MAX_MIN', self.maxlen, self.minlen)


if __name__ == "__main__":
    S = Stemmer()
    S.run()
