from natlog.natlog import *
from natlog.db import *
from natlog.parser import parse
#from natlog.scanner import Int
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

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

def wss2hotX(wss,mask) :
  mask=[mask]*len(wss[0])
  X=np.array(wss)
  Xplus=np.array(wss+[mask])
  print(Xplus.shape)
  enc=OneHotEncoder(handle_unknown='ignore')
  enc.fit(X)
  hotX=enc.transform(X).toarray()
  return enc,X,hotX

rf_learner=RandomForestClassifier(random_state=1234)
nn_learner=MLPClassifier(hidden_layer_sizes=(128,64,128))

class natlearner(natlog) :
  def __init__(self,
               text=None,
               file_name=None,
               tsv_file='out/texts/english.tsv',
               learner=nn_learner
               ):
    if not text and not file_name : text = ""
    super().__init__(text=text,file_name=file_name)
    self.mask='###'
    self.rels=tsv2db(fname=tsv_file)
    self.y0=np.array(self.rels.css)
    self.enc,self.X,self.hotX=wss2hotX(self.rels.css,self.mask)
    self.learner=learner

  def train(self):
    width=self.y0.shape[1]

    yargs=[self.hotX for _ in range(width)]
    y=np.concatenate(yargs,axis=0)

    maskColumn=np.array([self.mask]*self.X.shape[0])

    xargs=[]
    for i in range(width) :
      Xi=self.X.copy()
      Xi[:,i]=maskColumn
      xargs.append(Xi)

    X=np.concatenate(tuple(xargs),axis=0)
    X=self.enc.transform(X)

    print(X.shape,y.shape)
    return self.learner.fit(X,y)

  def ask(self,qss):
    Q=np.array(qss)


    for j in range(10): print('Q', j*10, Q[j*10])

    Q[0, 0] = self.mask
    Q[0, 3] = self.mask
    Q[0, 5] = self.mask

    Q[20, 0] = self.mask
    Q[20, 3] = self.mask
    Q[20, 5] = self.mask

    #Q[30, 0] = self.mask
    Q[30, 1] = self.mask
    Q[30, 2] = self.mask
    Q[30, 3] = self.mask
    #Q[30, 4] = self.mask
    #Q[30, 5] = self.mask


    hotQ=self.enc.transform(Q).toarray()

    assert hotQ.shape[1]==self.hotX.shape[1]

    hotA=(self.learner.predict(hotQ))

    print('\nANSWERS',hotA.shape,'\n')


    A=self.enc.inverse_transform(hotA)


    for j in range(10) : print('A',j*10,A[j*10])

    #print('!!!!',A)
    return A



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
  #qss=[['this','DET','det','NOUN','cat',nl.mask]]
  #nl.ask(qss)
  pass
