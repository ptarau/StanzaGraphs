from params import *
from summarizer import Summarizer
from rankers import ranker_dict
from textstar.textstar import textstar


class DeepSum(Summarizer):

    def summarize(self):  # extract summary and keywords
        g = super().to_nx()
        ranker = ranker_dict[PARAMS['RANKER']]
        sumsize = PARAMS['s_count']
        kwsize = PARAMS['k_count']
        trim = PARAMS['trim']
        sids, kwds, first_ranks = textstar(g, ranker, sumsize, kwsize, trim)
        sids.sort()
        kwds=self.extend_kwds(kwds,dict(first_ranks))
        sents = map(self.get_sent, sids)
        print("\nSUMMARY:")
        for sid, sent in zip(sids, sents): print(sent, '-> [', sid, ']')
        print("\nKEYWORDS:")
        for w in kwds: print(w, end='; ')
        print("\n")


def process_file(fname=None):
    nlp = DeepSum()
    nlp.from_file(fname)
    nlp.to_tsv()
    return nlp


def sumtest(fname='texts/english'):
    # nlp = Summarizer()
    # nlp.from_file(fname)
    t1 = timer()
    nlp = process_file(fname=fname)
    nlp.summarize()
    t2 = timer()
    print('PROCESSING TIME:', round(t2 - t1, 4))


if __name__ == "__main__":
    # simtest()
    sumtest(fname='texts/english')
    sumtest(fname='texts/cosmo')
