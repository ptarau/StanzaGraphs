import summarizer as nlp
import csv
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from collections import defaultdict, Counter
import math
from myfile import * 
from googletrans import Translator


# turns .tsv file into list of lists
def tsv2mat(fname) :
  with open(fname) as f:
     wss = csv.reader(f, delimiter='\t')
     return list(wss)

class Data :
  '''
  builds dataset from dependency edges in .tsv file associating
  <from,link,to> edges and sentences in which they occur;
  links are of the form POS_deprel_POS with POS and deprel
  tags concatenated
  '''
  def __init__(self,fname='texts/english') :
    edge_file="out/"+fname+".tsv"
    if not nlp.exists_file(edge_file) :
      nlp.process_file(fname=fname)

    wss = tsv2mat(edge_file)

    self.sents=tsv2mat("out/"+fname+"_sents.tsv")
    occs=defaultdict(set)
    sids=set()
    lens=[]
    for f,ff,r,tt,t,id in wss:
      id=int(id)
      if len(lens)<=id : lens.append(0)
      lens[id]+=1
      occs[(f,ff,r,tt,t)].add(id)
      sids.add(id)
    self.occs=occs # dict where edges occur
    self.lens=lens # number of edges in each sentence

    X,Y=list(zip(*list(occs.items())))
    X = np.array(X)
    y0 = np.array(sorted(map(lambda x:[x],sids)))

    # make OneHot encoders for X and y
    enc_X = OneHotEncoder(handle_unknown='ignore')
    enc_y = OneHotEncoder(handle_unknown='ignore')
    enc_X.fit(X)
    enc_y.fit(y0)
    hot_X = enc_X.transform(X).toarray()
    self.enc_X = enc_X
    self.enc_y = enc_y
    self.X=X
    # encode y as logical_or of sentence encodings it occurs in
    ms=[]
    for ys in Y :
      m = np.array([[0]],dtype=np.float32)
      for v in ys :
        m0=enc_y.transform(np.array([[v]])).toarray()
        m = np.logical_or(m,m0)
        m=np.array(np.logical_or(m,m0),dtype=np.float32)
      ms.append(m[0])
    hot_y=np.array(ms)

    self.hot_X=hot_X
    self.hot_y =hot_y

    print('\nFINAL DTATA SHAPES','X',hot_X.shape,'y',hot_y.shape)
    #print('SENTENCE LENGTHS',lens)

class Query(Data) :
  '''
  builds <from,link,to> dependency links form a given
  text query and matches it against data to retrive
  sentences in which most of those edges occur
  '''
  def __init__(self,fname='texts/english'):
    super().__init__(fname=fname)
    text = file2text(fname + ".txt")
    self.data_lang = nlp.detectLang(text)
    self.nlp_engine=nlp.NLP()

  def ask(self,text=None,interactive=False, tolang='en'):
    '''
    compute Jaccard similarity between
    set of edges in query and each sentence,
    then select the most similar ones
    '''
    if not text: text = input("Query:")
    elif not interactive: print("Query:",text)

    self.question_lang = nlp.detectLang(text)
    print('qLang:', self.question_lang)  
    print('Data Lang:',self.data_lang)

    if self.question_lang != self.data_lang:
      translator = Translator()
      if self.data_lang == 'zh':
        text= translator.translate(text, dest='zh-cn').text 
      elif self.data_lang == 'jv':
         text= translator.translate(text, dest='jw').text 
      else:
        text= translator.translate(text, dest=self.data_lang).text    
      print('translated question:\n', text)

    self.nlp_engine.from_text(text)
    sids=[]

    for f,ff,r,tt,t,_ in self.nlp_engine.facts() :
      sids.extend(self.occs.get((f,ff,r,tt,t),[]))
    self.save_answers(sids, tolang)

  def save_answers(self, sids, tolang, k=3):
    c = Counter(sids)
    qlen=len(list(self.nlp_engine.facts()))

    for id in c:
      shared=c[id]
      union_size=self.lens[id]+qlen-shared
      #jaccard=shared/union_size
      #c[id]=jaccard
      c[id]=shared/math.log(union_size)
    print('\nHIT WEIGHTS:', c, "\n")
    best = c.most_common(k)
    print('save_answers, question_lang:', self.question_lang, ', data_lang:\n', self.data_lang)
    translator = Translator()
    self.answer = defaultdict(set)
    for sid, _ in best:
      id, sent = self.sents[sid]
      print(id, ':', sent)
      if self.data_lang == tolang:
        self.answer[id] = sent
      else:      
        sent= translator.translate(sent, dest=tolang).text
        self.answer[id] = sent
    print("")


  def show_answers(self):
    print("\nSummary:")
    for id in self.answer:
      print(id, ':', self.answer[id])
    print("")


  def interact(self):
    while True:
      text = input("Query: ")
      if not text: return
      self.ask(text=text,interactive=True)


### TESTS ###

def qtest() :
  q=Query()
  q.ask(text="What did Penrose show?", tolang="en")
  q.show_answers()
  q.ask(text="What was in Roger's 1965 paper?", tolang="en")
  q.show_answers()

def dtest() :
  d=Data()
  print("X",d.hot_X.shape)
  print(d.hot_X)
  print("y",d.hot_y.shape)
  print(d.hot_y)

def dtests():
  ''' data loading tests'''
  dtest('out/texts/english.tsv')
  dtest('out/texts/spanish.tsv')
  dtest('out/texts/chinese.tsv')
  dtest('out/texts/russian.tsv')

def atest() :
  ''' tests symbolic and neural QA on given document '''
  '''
  i=Query('texts/english')
  print("\n")
  print("ALGORITHMICALLY DERIVED ANSWERS:\n")
  i.ask("What did Penrose show about black holes?")
  i.ask(text="What was in Roger's 1965 paper?")
  print("\n")
  '''
  
  i=Query('texts/chinese')
  print("\n")
  print("ALGORITHMICALLY DERIVED ANSWERS:\n")
  '''
  i.ask("中国藏书有多少年历史？")
  i.show_answers()
  i.ask(text="设立图书馆情报学本科教育的学校有多少所？")
  i.show_answers()
  '''
  i.ask("How many years is the Chinese collection of books?", tolang="en")
  i.show_answers()
  i.ask(text="How many schools have established undergraduate education in library and information science?", tolang="en")
  i.show_answers()
  print("\n")


if __name__=="__main__" :
  atest()
