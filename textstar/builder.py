# from multiprocessing import Pool, cpu_count
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import networkx as nx


# import pygraphviz

def stopwords():
    with open('stopwords.txt', 'r') as f:
        return set(l[:-1] for l in f.readlines())


def text2sents(text):
    lemmatizer = WordNetLemmatizer()
    stops = stopwords()
    sents = sent_tokenize(text)
    lss = []
    for sent in sents:
        ws = word_tokenize(sent)
        ls = []
        for w in ws:
            lw = w.lower()
            if not lw.isalpha(): continue
            if lw in stops: continue
            lemma = lemmatizer.lemmatize(w)
            if lemma in stops: continue
            ls.append(lemma)
        if not ls: continue
        lss.append((ls, sent))
    return lss


def sents2graph(lss):
    g = nx.DiGraph()
    g.add_edge(0, len(lss) - 1)  # first ot last sent
    for sent_id, (ls, _) in enumerate(lss):
        if sent_id > 0:  # from sent to sent before it
            g.add_edge(sent_id, sent_id - 1)
        g.add_edge(ls[0], sent_id)  # from 1-st word to sent id
        g.add_edge(sent_id, ls[-1])  # from sent id to last word
        # g.add_edge(ls[0], ls[-1]) # from first word to last word
        for j, w in enumerate(ls):
            if j > 0: g.add_edge(w, ls[j - 1])
    return g


def textstar(g, ranker, sumsize, kwsize, trim):
    while True:
        gbak = g.copy()

        print(gbak)

        unsorted_ranks = ranker(g)
        ranks = sorted(unsorted_ranks.items(), reverse=True, key=lambda x: x[1])
        total = len(ranks)
        split = trim * total // 100
        # print(ranks)
        weak_nodes = [n for (n, _) in ranks[split:]]
        weakest=weak_nodes[-1]
        weakest_rank=unsorted_ranks[weakest]
        for n in weak_nodes:
            g.remove_node(n)
        for n,r in ranks[0:split]:
            if r<=weakest_rank:
                g.remove_node(n)
        s_nodes = len([n for n in g.nodes if isinstance(n, int)])
        w_nodes = g.number_of_nodes() - s_nodes

        print('=> S_NODES:', s_nodes, 'W_NODES',w_nodes)

        if s_nodes <= sumsize: break
        if w_nodes <= kwsize: break
    return gbak, ranks


short_text = """ 
    I ate dinner. 
    We had a three-course meal.
    Brad came to dinner with us.
    He loves fish tacos.
    In the end, we all felt like we ate too much.
    We all agreed; it was a magnificent evening.
    """


def process_text(text, ranker=nx.betweenness_centrality, sumsize=5, kwsize=7, trim=80):
    lss = text2sents(text)
    print(len(lss))
    # print(lss)
    g = sents2graph(lss)
    print(g)
    # for f,t in g.edges(): print(t,'<-',f)
    g, ranks = textstar(g, ranker, sumsize, kwsize, trim)
    sids = sorted([sid for (sid, _) in ranks if isinstance(sid,int)])
    sids = sids[0:sumsize]
    print("SIDS:",sids)
    all_sents = [sent for (_, sent) in lss]
    sents = [(i,all_sents[i]) for i in sids]
    kwds = [w for (w,_) in ranks if isinstance(w, str)][0:kwsize]

    if g.number_of_edges() < 600:
        nx.nx_agraph.write_dot(g, 'pic.gv')

    return sents, kwds


def test_builder():
    with open('../texts/english.txt', 'r') as f:
        text = f.read()
    sents, kwds = process_text(text=text,ranker=nx.pagerank)
    print('SUMMARY:')
    for sent in sents:
        print(*sent)
    print('\nKEYWORDS:')
    print("; ".join(kwds)+".")


if __name__ == "__main__":
    # print(stopwords())
    test_builder()
