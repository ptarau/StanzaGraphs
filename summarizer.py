import stanza
import csv
import os
import networkx as nx
from visualizer import gshow,xshow

from collections import defaultdict

# alternative rankers

def rank_with(f,g) :
  return f(g)

def pagerank(g) :
  return nx.pagerank(g)

def subg(g) :
  g=g.to_undirected()
  return nx.subgraph_centrality(g)

def closeness(g) :
  return nx.closeness_centrality(g)

def betweenness(g) :
  return nx.betweenness_centrality(g)

def current_flow(g) :
  u=g.to_undirected()
  return nx.current_flow_betweenness_centrality(u)

def hits(g) :
  (hubs,auths)=nx.hits_numpy(g)
  ranks=dict()
  for x in g.nodes():
    if isinstance(x,int) :
      ranks[x]=hubs[x]
    else :
      ranks[x]=auths[x]
  return ranks

class NLP :
  '''
  stanza-based multi-lingual NLP processor
  that extracts summaries and keywords
  and builds text graph edge files derived
  from dependency links usable donwstream
  for algorithmic and deep-learning based
  information retrieval tasks
  '''
  def __init__(self,lang='en'):
    if not exists_file(home_dir()+'/stanza_resources/'+lang):
      stanza.download(lang)
    self.nlp = stanza.Pipeline(lang=lang,logging_level='WARN')
    ensure_path("out/")
    ensure_path("pics/")


  # process text from a file
  def from_file(self,fname='texts/english'):
    self.fname=fname
    text = file2text(fname + ".txt")
    self.doc = self.nlp(text)

  def from_text(self,text="Hello!"):
    self.doc = self.nlp(text)

  def keynoun(self,x):
    '''true for "important" nouns'''
    return  x.upos == 'NOUN' and ('subj' in x.deprel or 'ob' in x.deprel)

  def facts(self):
    '''generates <from,link,to,sentence_id> tuples'''
    def fact(x,sent,sid) :
      if x.head==0 :
        yield x.lemma,x.upos+'_PREDICATE_OF',sid,sid
      else :
        hw=sent.words[x.head-1]
        if self.keynoun(x) : # reverse link to prioritize key nouns
          yield hw.lemma, hw.upos + "rev_"+x.deprel + x.upos, x.lemma, sid
          yield (sid, 'ABOUT', x.lemma, sid)
        else:
          yield x.lemma,x.upos+x.deprel+hw.upos,hw.lemma,sid
        if  x.deprel in ("compound","flat") :
          comp = x.lemma+" "+hw.lemma
          yield x.lemma, x.upos+"inCOMPOUND", comp, sid
          yield hw.lemma, hw.upos + "inCOMPOUND", comp, sid
          yield (sid, 'ABOUT', comp, sid)


    for sid,sent in enumerate(self.doc.sentences) :
      for x in sent.words :
        yield from fact(x,sent,sid)

  def keynouns(self):
    '''collects important nouns'''
    ns=set()
    for sent in self.doc.sentences:
      for x in sent.words:
        if self.keynoun(x) :
          ns.add(x.lemma)
    return ns

  def context_dict(self):
    contexts=defaultdict(list)
    for sid,sent in enumerate(self.doc.sentences):
      ws=list(sent.words)
      good = ('NOUN', 'ADJ')
      for i,w in enumerate(ws):
        if not w.upos in good : continue
        if i==0 or i+1==len(ws) : continue
        prev_w=ws[i-1]
        next_w=ws[i+1]
        context=[w.lemma]
        if prev_w.upos in good :
          context = [prev_w.lemma]+context
        if  next_w.upos in good :
           context.append(next_w.lemma)
        if len(context)<2 : continue
        #phrase=" ".join(context)
        contexts[w.lemma].append((sid,context))
    return contexts


  def info(self,wk=8,sk=6,ranker=subg):
    '''extract keywords and summary sentences'''
    g = self.to_nx()
    ranks = rank_with(ranker, g)

    def rank_phrase(pair):
      sid, ws = pair
      r = sum(ranks[x] for x in ws if x in ranks)
      #print('!!!sum', r)
      r = r * ranks[sid]
      #print('!!!prod', r)
      return (r, ws)

    def extend_kwd(w):
      cs=contexts[w]
      if not cs: return w
      rs=map(rank_phrase,cs)
      rs=sorted(rs,reverse=True,key=lambda x : x[0])
      phrase=" ".join(rs[0][1])
      return phrase

    ns=self.keynouns()

    contexts = self.context_dict()
    #print('!!!', len(contexts))

    kwds,sids,picg=ranks2info(g,ranks,ns,wk,sk)
    kwds=set(map(extend_kwd,kwds))

    sents=list(map(self.get_sent,sorted(sids)))
    return kwds,sents,picg

  def to_nx(self): # converts to networkx graph
    return facts2nx(self.facts())

  def show(self,k=20):
    ''' visualize  nodes and edges'''
    g = self.to_nx()
    gshow(g,file_name="pics/"+self.fname+".gv")

  def to_tsv(self): # writes out edges to .tsv file
    facts2tsv(self.facts(),"out/"+self.fname+".tsv")
    self.to_sents()

  def to_prolog(self): # writes out edges to Prolog file
    facts2prolog(self.facts(),"out/"+self.fname+".pro")

  def get_sent(self,sid) :
    return self.doc.sentences[sid].text

  # writes out sentences
  def to_sents(self):
    def sent_gen() :
       for sid,sent in enumerate(self.doc.sentences):
         yield sid,sent.text
    facts2tsv(sent_gen(),"out/"+self.fname+"_sents.tsv")


  def summarize(self,wk=8,sk=5) : # extract summary and keywords
    kws,sents,picg=self.info(wk,sk)
    print("\nSUMMARY:")
    for sent in sents : print(sent)
    print("\nKEYWORDS:")
    for w in kws : print(w,end='; ')
    print("\n")
    gshow(picg,file_name='pics/'+self.fname+'.gv')



# read a file into a string text
def file2text(fname) :
  with open(fname,'r') as f:
    return f.read()

def facts2nx(fgen) :
   '''
   turns edges into networkx DiGraph
   edges also contain "root" links to
   sentence they originate from
   '''
   g=nx.DiGraph()
   for f,rel,t,id in fgen :
     g.add_edge(f,t)
   return g

# uses rank dictionary to extract salient
# sentences and keywords
def ranks2info(g,ranks,keyns,wk,sk) :
  ranked=sorted(ranks.items(),key=(lambda x: x[1]),reverse=True)
  sids=[]
  kwds=[]
  for x, r in ranked:
    if wk<=0 : break
    if isinstance(x,str) and x in keyns:
      kwds.append(x)
      wk-=1
  for x,r in ranked:
    if sk <= 0: break
    if isinstance(x, int):
      sids.append(x)
      sk -= 1

  _,minr=ranked[(len(ranked)-1)//4]
  good = [x for (x,r) in ranked
          if isinstance(x,str)
             #and x.isalpha()
             and len(x)>1
             and (r>minr or x in keyns)]
  picg = nx.DiGraph()
  for (x,y) in g.edges() :
    if x in good and y in good :
      picg.add_edge(x,y)
  return kwds,sids,picg

# writes out edge facts as .tsv file
def facts2tsv(fgen,fname) :
  ensure_path(fname)
  with open(fname, 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    for fact in fgen:
      writer.writerow(fact)

# writes out edge facts as Prolog file
def facts2prolog(fgen,fname) :
  ensure_path(fname)
  with open(fname, 'w') as f:
    for fact in fgen:
      print('edge',end='',file=f)
      print(fact,end=".\n",file=f)

def exists_file(fname) :
  ''' if it exists as file or dir'''
  return os.path.exists(fname)

def home_dir() :
  from pathlib import Path
  return str(Path.home())

def ensure_path(fname) :
  dir,_=os.path.split(fname)
  os.makedirs(dir, exist_ok=True)


def process_file(fname='texts/english',lang='en') :
  nlp = NLP(lang)
  nlp.from_file(fname)
  nlp.to_tsv()
  return nlp

# TESTS

def test(fname='texts/english',lang='en') :
  nlp=NLP(lang)
  nlp.from_file(fname)
  nlp.to_tsv()
  nlp.to_prolog()
  nlp.summarize()

if __name__=="__main__" :
  test(fname='texts/english',lang='en')
  test(fname='texts/spanish',lang='es')
  test(fname='texts/chinese',lang='zh-hans')
  test(fname='texts/russian',lang='ru')
