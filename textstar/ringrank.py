# from multiprocessing import Pool, cpu_count
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

import networkx as nx


# import pygraphviz

def stopwords():
    with open('stopwords.txt', 'r') as f:
        return set(line[:-1] for line in f.readlines())


def good_sent(ws):
    # print('>>>', ws)
    good = 0
    bad = 0
    if len(ws) > 256: return False
    for w in ws:
        if w.isalpha() and len(w) > 1 or w in ".?!":
            good += 1
        else:
            bad += 1
    if good / (1 + bad + good) < 0.66: return False
    return True


def text2sents(text):
    lemmatizer = WordNetLemmatizer()
    stops = stopwords()
    sents = sent_tokenize(text)
    lss = []
    for sent in sents:
        ws = word_tokenize(sent)
        if not good_sent(ws):
            continue

        wts = pos_tag(ws)

        ls = []
        for w, t in wts:
            lw = w.lower()
            if not lw.isalpha(): continue
            if lw in stops: continue
            lemma = lemmatizer.lemmatize(w)
            if lemma in stops: continue
            tag = t[0]
            ls.append(W(lemma, w, tag))
        if not ls: continue
        lss.append((ls, sent))
    return lss


class W:
    def __init__(self, lemma, word, tag):
        self.lemma = lemma
        self.word = word
        self.tag = tag

    def __repr__(self):
        return f"W('{self.lemma}','{self.word}','{self.tag}')"


def sents2graph(lss):
    g = nx.DiGraph()
    g.add_edge(0, len(lss) - 1)  # first to last sent
    for sent_id, (ls, _) in enumerate(lss):
        if sent_id > 0:  # from sent to sent before it
            g.add_edge(sent_id, sent_id - 1)
        g.add_edge(ls[0].lemma, sent_id)  # from 1-st word to sent id
        g.add_edge(sent_id, ls[-1].lemma)  # from sent id to last word
        # g.add_edge(ls[0], ls[-1]) # from first word to last word
        for j, w in enumerate(ls):
            if j > 0: g.add_edge(w.lemma, ls[j - 1].lemma)
    return g


def textstar(g, ranker, sumsize, kwsize, trim):
    assert sumsize > 0 or kwsize > 0
    final_sids, final_kwds = None, None
    first_ranks = None

    while True:

        unsorted_ranks = ranker(g)
        ranks = sorted(unsorted_ranks.items(), reverse=True, key=lambda x: x[1])

        if first_ranks is None: first_ranks = ranks

        sids = [sid for (sid, _) in ranks if isinstance(sid, int)]
        kwds = [w for (w, _) in ranks if not isinstance(w, int)]

        s_done = len(sids) <= sumsize
        w_done = len(kwds) <= kwsize

        if not s_done:
            final_sids = sids
        if not w_done:
            final_kwds = kwds

        if s_done and w_done: break

        print('=> S_NODES:', len(sids), 'W_NODES', len(kwds))

        total = len(ranks)
        split = trim * total // 100
        # print(ranks)
        weak_nodes = [n for (n, _) in ranks[split:]]

        if weak_nodes:
            weakest = weak_nodes[-1]
            weakest_rank = unsorted_ranks[weakest]
            for n in weak_nodes:
                g.remove_node(n)
            for n, r in ranks[0:split]:
                if r <= weakest_rank:
                    g.remove_node(n)

    return final_sids, final_kwds, first_ranks


def process_text(text, ranker, sumsize, kwsize, trim, show):
    lss = text2sents(text)
    print("#SENT:", len(lss))

    g0 = sents2graph(lss)
    print('GRAPH:', g0)
    g=g0.copy()

    if show and g.number_of_edges() < 600:
        print('::::', g.number_of_nodes())
        nx.nx_agraph.write_dot(g, 'text.gv')

    all_sents = [sent for (_, sent) in lss]

    if len(lss) < sumsize:
        print('text too small to summarize', text)
        return [], [], g, all_sents

    # for f,t in g.edges(): print(t,'<-',f)
    final_sids, final_kwds, _ = textstar(g, ranker, sumsize, kwsize, trim)

    sids = final_sids[0:sumsize]
    sids = sorted(sids)
    print("SIDS:", sids)

    sents = [(i, all_sents[i]) for i in sids]

    kwds = final_kwds[0:2 * kwsize]

    clean_kwds = []
    for i, u in enumerate(kwds):
        if isinstance(u, str):
            redundant = False
            for j in range(0, kwsize):
                v = kwds[j]
                if isinstance(v, tuple) and u in v:
                    redundant = True
                    break
            if not redundant: clean_kwds.append(u)
        else:
            clean_kwds.append(" ".join(u))
    return sents, clean_kwds[0:kwsize], g0, all_sents


def summarize(fname, ranker=nx.pagerank, sumsize=6, kwsize=6, trim=80, show=False):
    with open(fname + ".txt", 'r') as f:
        text = f.read()

    return process_text(text, ranker, sumsize, kwsize, trim, show)


# for x in kslide(list(range(6))): print(x)
def kslide(ws):
    ws_ws = ws + ws
    for k in range(len(ws), 0, -1):
        for i in range(len(ws)):
            yield ws_ws[i:i + k]

def near_in(g,x):
    return set(g.successors(x)).union(g.predecessors(x))

def query(all_sents, g, text):
    def sent_id(w):
        lim = g.number_of_nodes()
        ns = near_in(g,w)
        for _ in range(lim):
            found = False
            for r in ns:
                if isinstance(r, int):
                    found = True
                    yield r
            if found: return
            ms = set()
            for n in ns:
                xs = near_in(g,n)
                ms = ms.union(xs)
            ns = ns.union(ms)

    def walk(ns):
        print('!!!!NS:',ns)
        rs = []
        for i, n in enumerate(ns):
            f = ns[i]

            if f not in g.nodes: break
            #print('there',rs)
            rs.append(f)
            #xs = set(g.successors(f))
            xs = near_in(g,f)
            print("@@@@xs:",f,xs)
            if not xs: break
            if i + 1 > len(ns) - 1: break
            t = ns[i + 1]
            if t not in xs: return
        if rs:
            last = rs[-1]
            print('LAST:',last)
            yield rs, list(sent_id(last))

    lss = text2sents(text)
    ls = lss[0][0]
    ws = [w.lemma for w in ls]

    ws.reverse()
    print('WORDS:', ws)

    for ns in kslide(ws):
        for rs, sids in walk(ns):
            for sid in sids:
                yield all_sents[sid]
            return


def run_textstar(name, q=None):
    sents, kwds, g, all_sents = summarize(name, show=True)

    print('SUMMARY:')
    for sent in sents:
        print(*sent)
    print('\nKEYWORDS:')
    # print("; ".join(kwds) + ".")
    print(kwds)
    print()
    read=False
    if q is None:
        q = input('Query: ')
        read=True
    if q:
        if not read: print('Query: ', q)
        found=False
        for a in query(all_sents, g, q):
            found=True
            print('ANSWER:',a)
            print('')
        if not found:
           print('ANSWER: ','I do not know.')
           print('')

def test_texstar():
    run_textstar('../texts/short', q='Who laughed at Steven?')
    run_textstar('../texts/short', q='Was the store closed?')
    run_textstar('../texts/goedel',q='What did his friends tell Gödel?')
    return
    run_textstar('../texts/small', q='What happened in a restaurant?')
    run_textstar('../texts/english', q='What did the Nobel committee do?')
    run_textstar('../texts/cosmo',q="What's new about field equations?")




if __name__ == "__main__":
    test_texstar()
