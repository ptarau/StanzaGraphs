import numpy as np
from sklearn.datasets import make_classification
from torch import nn
import torch
import skorch
from params import *
from answerer import Data
from sk_answerer import Trainer, Inferencer

# JUST a PROOF OF CONCEPT -
# skorch does not support (esily) multiple co-dependent outputs
# to fix, most likely, we must override the torch forward method

class ClassifierModule(nn.Module):
  def __init__(
      self,
      num_units=32,
      nonlin=torch.sigmoid,
      dropout=0.5,
  ):
    super(ClassifierModule, self).__init__()
    self.num_units = num_units
    Xsize=ClassifierModule.Xsize
    self.nonlin = nonlin
    self.dropout = dropout

    self.dense0 = nn.Linear(Xsize, num_units)
    self.nonlin = nonlin
    self.dropout = nn.Dropout(dropout)
    self.dense1 = nn.Linear(num_units, num_units)
    self.output = nn.Linear(num_units, 2)

  def forward(self, X):
    X = self.nonlin(self.dense0(X))
    #X = self.dropout(X)
    X = self.nonlin(self.dense1(X))
    #X = self.dropout(X)
    #X = self.nonlin(self.dense1(X))
    X = torch.softmax(self.output(X), dim=-1)
    return X

class TorchClassifier :
  def __init__(self,max_epochs=20,lr=0.05):
    self.max_epochs=max_epochs
    self.lr=lr

  def fit(self,X,y,**fit_params):
    X=X.astype(np.float32)
    y=y.astype(np.int64)

    ClassifierModule.Xsize = X.shape[-1]
    ClassifierModule.ysize = y.shape[-1]

    l=ClassifierModule.ysize

    nets = [None] * l
    for i in range(l):
      net = skorch.NeuralNetClassifier(
        ClassifierModule,
        max_epochs=self.max_epochs,
        lr=self.lr
        #train_split=skorch.dataset.CVSplit(5, stratified=False)
        #     device='cuda',  # uncomment this to train with CUDA
      )
      nets[i] = net.fit(X, y[:, i],**fit_params)

    self.nets=nets



  def predict_proba(self,X):
    X = X.astype(np.float32)
    l = ClassifierModule.ysize
    nets = self.nets
    p = [0] * l
    # TODO - this is just a sketch - NOT RIGHT
    for i in range(l):
      p[i] = nets[i].predict_proba(X)
    p=np.array(p)
    #ppp(p.shape)
    prob = np.mean(p, axis=-1)
    prob = prob / l

    prob=np.array((prob,))
    #prob.reshape((1,-1))

    #ppp(prob.shape)

    return prob


  def predict(self,X):
    p=self.predict_proba(X)
    y= p.argmax(axis= -1)
    return y

class SkorchTrainer :
  def __init__(self, X,y,**kwargs):
    self.classifier=TorchClassifier(**kwargs)
    self.classifier.fit(X,y)

class SkorchAnswerer(Inferencer) :
  def __init__(self, fname='texts/english'):
    super().__init__(fname=fname)
    #self.trainer = self.make_trainer(self.hot_X, self.hot_y)

  def make_trainer(self, X, y):
    return SkorchTrainer(X, y)

def old_test() :
  def make_data():
    data = Data()
    X = data.hot_X
    y = data.hot_y
    X, y = X.astype(np.float32), y.astype(np.int64)
    return X, y

  clf = TorchClassifier()
  X, y = make_data()
  #X, y = X.astype(np.float32), y.astype(np.int64)
  clf.fit(X,y)
  prob=clf.predict(X)
  print(prob)

def atest() :
  i = SkorchAnswerer()
  print("\n\n")
  print("ALGORITHMICALLY DERIVED ANSWERS:\n")
  i.ask("What did about black holes?")
  i.ask(text="What was in Roger's 1965 paper?")
  print("\n")
  print("NEURAL NET'S ANSWERS:\n")
  i.query("What did Penrose show about black holes?")
  i.query(text="What was in Roger's 1965 paper?")


if __name__=="__main__" :
  #tntest()
  atest()
