import networkx as nx

from params import *
from textdeps import TextWorker
from visualizer import gshow


class Converter:
    def __init__(self, pics=None, links=1, mock=None):
        self.g = from_pickle(PARAMS['DATA_CACHE'] + 'arxiv.pickle')
        self.mock = mock
        if pics is None:
            pics = set(1 << i for i in range(30))
        self.pics = pics

        self.tm = TextWorker()
        self.links = links
        self.prolog_file = PARAMS['OUTPUT_DIRECTORY'] + 'arxiv_all.pro'
        self.fact_file = PARAMS['OUTPUT_DIRECTORY'] + 'arxiv_all_facts.pro'

    def facts_of(self, n):
        gn = self.g.nodes[n]
        for fact in self.tm.facts():
            # yield (n,gn["kind"],gn["y"]) + fact
            yield (n,) + fact

    def term_of(self, n, text):
        g = self.g
        self.tm.from_text(text)
        dep_dag = self.tm.to_nx_tree()
        if n in self.pics:
            gshow(dep_dag, file_name=PARAMS['PICS'] + str(n) + ".gv")
        t = self.tm.as_term()
        xs = [str(n), g.nodes[n]["kind"], g.nodes[n]["y"][0], t]
        if self.links:
            ms = list(nx.neighbors(g, n))
            xs.append(str(ms))
        args = ",".join(xs)
        return 'at(' + args + ').'

    def run(self):
        ctr = 0
        gd = self.g.nodes
        with open(self.prolog_file, 'wt') as pout:
            with open(self.fact_file, 'wt') as fout:
                if self.mock:
                    m = self.g.number_of_nodes()
                    ns = set(m - n - 1 for n in range(self.mock))
                    xs = set(x for n in ns for x in nx.all_neighbors(self.g, n))
                    ns = ns | xs
                    print('NODES PICKED in mock:', ns)
                else:
                    ns = self.g.nodes

                print(
                    "% at(node_id, tr/va/te, label, prolog_term, neighbors_list)",
                    file=pout)
                print(
                    "% at(node_id, from_lemma, from_tag, dep_rel, to_tag, to_lemma, pos_no, sent_id",
                    file=fout)

                for n in ns:
                    if self.mock or n % 100 == 0: print('DIGESTING:', n)
                    title = gd[n]['title']
                    abstr = gd[n]['abstr']
                    text = title + ". " + abstr
                    text = text.lower()
                    term = self.term_of(n, text)
                    print(term, file=pout)
                    for fact in self.facts_of(n):
                        print('at', end='', file=fout)
                        print(fact, end=".\n", file=fout)
                    ctr += 1


if __name__ == "__main__":
    C = Converter(mock=5)
    C.run()
