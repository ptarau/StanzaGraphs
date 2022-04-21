# from multiprocessing import Pool, cpu_count
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
#import graphviz

import os
import openai
#POST https://api.openai.com/v1/engines/{text-davinci-002}/edits
#Authorization: Bearer YOUR_API_KEY

openai.api_key_path = "textstar/.env"
#openai.api_key = os.getenv("OPENAI_API_KEY")

'''
openai_object = openai.Engine.list()
#print(openai_object)

openai_object = openai.Completion.create(
  engine="text-babbage-001",
  prompt="Say this is a test",
  max_tokens=5
)

'''
openai_object = openai.Edit.create(
  engine="text-davinci-edit-001",
  input=" -LRB- CNN -RRB- -- The 54 men and 14 boys rescued after being found chained this week at an Islamic religious school in Pakistan have been reunited with their families or placed in shelters , authorities said . The group was discovered in an underground room with heavy chains linking them together . Officials said the facility was part madrassa and part drug-rehab facility , and the captives were chained at night apparently to prevent their escape . The operation was successful , and we plan on continuing our work to ensure that places like this are shut down , ' Marwat said . Many of the captives told police their families sent them there because they were recovering drug addicts .     But the future of the rescued children was unclear .",
  instruction="Simplification"
)

print(openai_object)

import networkx as nx
import json

import pygraphviz




def stopwords():
    with open('textstar/stopwords.txt', 'r') as f:
        return set(l[:-1] for l in f.readlines())


def good_sent(ws):
    good = 0
    bad = 0
    if len(ws) > 256: return False
    for w in ws:
        if w.isalpha() and len(w) > 1:
            good += 1
        else:
            bad += 1
    if good / (1 + bad + good) < 0.75: return False
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


def add_compounds(g, sid, ls):
    cs = 0
    m = len(ls)
    added = set()
    for i, w in enumerate(ls):
        if i < m - 2 and w.tag in 'RJ' and ls[i + 1].tag in 'J' and ls[i + 2].tag in 'N':
            #t = " ".join([w.word, ls[i + 1].word, ls[i + 2].word])
            t = (w.word, ls[i + 1].word, ls[i + 2].word)
            for x in ls[i:i + 3]:
                f = x.lemma
                g.add_edge(f, t)
                added.add(i)
                added.add(i + 1)
                added.add(i + 2)
                g.add_edge(sid, t)
        elif i < m - 1 and i not in added and (i + 1) not in added and \
            w.tag in 'NJ' and ls[i + 1].tag in 'N':
            for x in ls[i:i + 2]:
                f = x.lemma
                #t = " ".join([w.word, ls[i + 1].word])
                t=(w.word, ls[i + 1].word)
                g.add_edge(f, t)
                g.add_edge(sid, t)


def sents2graph(lss):
    g = nx.DiGraph()
    g.add_edge(0, len(lss) - 1)  # first ot last sent
    for sent_id, (ls, _) in enumerate(lss):
        if sent_id > 0:  # from sent to sent before it
            g.add_edge(sent_id, sent_id - 1)
        g.add_edge(ls[0].lemma, sent_id)  # from 1-st word to sent id
        g.add_edge(sent_id, ls[-1].lemma)  # from sent id to last word
        # g.add_edge(ls[0], ls[-1]) # from first word to last word
        for j, w in enumerate(ls):
            if j > 0: g.add_edge(w.lemma, ls[j - 1].lemma)
        add_compounds(g, sent_id, ls)
    return g


def textstar(g, ranker, sumsize, kwsize, trim):
    assert sumsize > 0 or kwsize > 0
    final_sids, final_kwds = None, None
    first_ranks=None

    while True:

        unsorted_ranks = ranker(g)
        ranks = sorted(unsorted_ranks.items(), reverse=True, key=lambda x: x[1])

        if first_ranks is None : first_ranks=ranks

        sids = [sid for (sid, _) in ranks if isinstance(sid, int)]
        kwds = [w for (w, _) in ranks if not isinstance(w, int)]

        # trim kwds occurrring in compound others

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

    g = sents2graph(lss)
    print(g)

    if show and g.number_of_edges() < 600:
        nx.nx_agraph.write_dot(g, 'pic.gv')


    # for f,t in g.edges(): print(t,'<-',f)
    final_sids, final_kwds,_ = textstar(g, ranker, sumsize, kwsize, trim)

    sids = final_sids[0:sumsize]
    sids = sorted(sids)
    print("SIDS:", sids)
    all_sents = [sent for (_, sent) in lss]
    sents = [(i, all_sents[i]) for i in sids]

    kwds = final_kwds[0:2*kwsize]

    clean_kwds=[]
    for i,u in enumerate(kwds):
        if isinstance(u,str):
           redundant=False
           for j in range(0,kwsize):
              v = kwds[j]
              if isinstance(v,tuple) and u in v:
                  redundant=True
                  break
           if not redundant : clean_kwds.append(u)
        else:
            clean_kwds.append(" ".join(u))

    return sents, clean_kwds[0:kwsize]


def summarize(fname, ranker=nx.pagerank, sumsize=6, kwsize=6, trim=80, show=True):

    with open(fname + ".txt", 'r') as f:
        text = f.read()
    sents, kwds = process_text(text, ranker, sumsize, kwsize, trim, show)

    return sents, kwds


def test_textstar(name):
    #sents, kwds = summarize('../texts/english', show=True)
    sents, kwds = summarize(name, show=True)

    print('SUMMARY:')
    for sent in sents:
        print(*sent)
    print('\nKEYWORDS:')
    #print("; ".join(kwds) + ".")
    print(kwds)


if __name__ == "__main__":
    test_textstar('dataset/cnn_big/docsutf8/00a2aef1e18d125960da51e167a3d22ed8416c09')
    #test_textstar('dataset/cosmo')
    
