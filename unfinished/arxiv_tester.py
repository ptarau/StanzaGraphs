from collections import defaultdict
from summarizer import *


class Tester(Summarizer):
    def __init__(self):
        super().__init__(lang='en')

    def run(self, fname='experiments/arxiv.pickle'):
        ensure_path('experiments/out/no_such_file')
        g = from_pickle(fname)
        nlp = self.nlp
        wcount=defaultdict(set)
        with open('experiments/out/kwds.tsv', 'wt') as wf:
            for n in g.nodes():
                title = g.nodes[n]['title']
                abstr = g.nodes[n]['abstr']
                text = title + ". " + abstr
                T.from_text(text, detect=False)
                kws, sids, sents, picg = self.info(wk=6,sk=3)
                for w in kws:
                    wcount[w].add(n)
                line="\t".join(kws)
                print(line,file=wf)
                if n % 100 == 0: print(n)
                if n>4000 : break
        with open('experiments/out/counts.tsv','wt') as cf:
          wks=[]
          for w,ks in wcount.items():
              wks.append((w,sorted(list(ks))))
              print(w+'\t'+str(len(ks)),file=cf)
          wks.sort(reverse=True,key=lambda x: len(x[1]))
          to_json(wks,'experiments/out/where.json')



if __name__ == "__main__":
    T = Tester()
    T.run()
