import numpy as np

from params import *
from summarizer import Summarizer
from univsims import UnivSims


class SumarizerWithSims(Summarizer):

    def to_sims(self):
        sents = [sent for (_, sent) in self.sent_gen()]
        size = len(sents)
        B = UnivSims()
        _, embs = B.digest(sents)
        M = np.zeros([size, size])
        for i in range(size):
            for j in range(i):
                    M[i, j] = B.similarity(embs[i], embs[j])
        return M

    def to_nx(self):  # converts to networkx graph
        g=super().to_nx()
        n=PARAMS["MINSIM"]
        M=self.to_sims()
        m=2*n*np.mean(M) # as half are 0
        n=M.shape[1]
        for i in range(n):
            for j in range(i):
                w=M[i,j]
                if w>m:
                    w=1-w # interpret w as a distance
                    len_i = len(self.get_sent(i))
                    len_j = len(self.get_sent(j))
                    if len_j<=len_i:
                       g.add_edge(i,j,weight=w)
                       #print('!!!', i, j, w)
                    else:
                       #print('!!!', j, i, w)
                       g.add_edge(j, i, weight=w)

        # alternatives to experiment with:
        """
           add edges for all high enough similarities
           the same  but only for close sentences
           add endges only from longer to shorter sentence  (as is now)
           add edges only from later to earlier sentence
        """
        return g

def process_file_with_sims(fname=None):
    nlp = SumarizerWithSims()
    nlp.from_file(fname)
    nlp.to_tsv()
    return nlp


def simtest(fname='texts/english'):
    nlp = process_file_with_sims(fname=fname)
    M=nlp.to_sims()
    print(M.shape)
    print(M)

def sumtest(fname='texts/english'):
    # nlp = Summarizer()
    # nlp.from_file(fname)
    t1=timer()
    nlp = process_file_with_sims(fname=fname)
    nlp.summarize()
    t2 = timer()
    print('PROCESSING TIME:', round(t2 - t1, 4))

if __name__ == "__main__":
    #simtest()
    sumtest(fname='texts/cosmo')
