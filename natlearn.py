from natlog.natlog import *
from natlog.db import *
from natlog.parser import parse
#from natlog.scanner import Int
from sklearn.ensemble import RandomForestClassifier

from answerer import tsv2mat
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# WORK IN PROGRESS, TODO "

def tsv2db(fname='out/texts/english.tsv'):
  rels=db()
  wss = tsv2mat(fname)
  for ws in wss: rels.add_db_clause(ws)
  #rels.load_tsv(fname)
  return rels

def wss2hotXy(wss,io_split = -1) :
  Xy=np.array(wss)
  X=Xy[:,:io_split]
  y=Xy[:,io_split:]
  print(X.shape,y.shape)

  enc=OneHotEncoder(handle_unknown='ignore')
  enc.fit(X)
  hotX=enc.transform(X).toarray()

  enc_ = OneHotEncoder(handle_unknown='ignore')
  enc_.fit(y)
  hoty = enc_.transform(y).toarray()

  #print(hotX.shape,hoty.shape)
  #coldX=enc.inverse_transform(hotX)
  #print(coldX[0])
  return enc,hotX,enc_,hoty

def wss2hotX(wss,io_split = -1) :
  X=np.array(wss)
  print(X.shape)
  enc=OneHotEncoder(handle_unknown='ignore')
  enc.fit(X)
  hotX=enc.transform(X).toarray()

  return enc,hotX

class natlearner(natlog) :
  def __init__(self,
               text=None,
               file_name=None,
               tsv_file='out/texts/english.tsv',
               learner=RandomForestClassifier(random_state=1234)
               ):
    if not text and not file_name : text = ""
    super().__init__(text=text,file_name=file_name)
    self.rels=tsv2db(fname=tsv_file)
    self.enc,self.hotX=wss2hotX(self.rels.css)
    self.learner=learner

  def train(self):
    return self.learner.fit(self.hotX,self.hotX)

  def ask(self,qss):
    Q=np.array(qss)
    print('###',Q.shape)
    hotQ=self.enc.transform(Q).toarray()

    assert hotQ.shape==self.hotX.shape

    # TODO


# tests

def qtest():
  rels=tsv2db()
  for m in rels.match_of((0,'ADJ',2,'NOUN',4,'8')):
    print(m)
  print('')
  for m in rels.match_of((0,1,'flat',1,4,5)):
    print(m)
  print('')
  code='''
      goal X U : ~ X Y flat Y Z U .
    '''
  logic_engine=natlog(text=code)
  logic_engine.db=rels

  #logic_engine.query("~ _X Y flat Y _Z U?")
  logic_engine.query("goal X U?")

def py_test() :
  nd = natlog(file_name="natprogs/inter.nat")
  print('RULES')
  print(nd)
  nd.query("goal X?")



if __name__=="__main__" :
  #py_test()
  #qtest()
  nl=natlearner()
  nl.train()
  nl.ask(nl.rels.css)
  pass
