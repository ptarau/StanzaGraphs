import numpy as np

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
            for j in range(size):
                if i < j:
                    M[i, j] = B.similarity(embs[i], embs[j])
        return M

    def to_nx(self):  # converts to networkx graph
        g=super().to_nx()
        #M=self.to_sims()
        # add here similarity links
        """
           add all similarities
           add those in close sentences
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


if __name__ == "__main__":
    simtest()
