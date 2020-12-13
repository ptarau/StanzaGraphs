from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from answerer import Data,Query

class Trainer() :
  def __init__(self, hot_X,hot_y):
    self.classifier=RandomForestClassifier(n_estimators=100, n_jobs=16)
    self.classifier.fit(hot_X, hot_y)

class Inferencer(Query) :
  '''
  loads model trained on associating dependency
  edges to sentences in which they occur
  '''
  def __init__(self,fname='texts/english',lang='en'):
    super().__init__(fname=fname,lang=lang)
    self.trainer=Trainer(self.hot_X,self.hot_y)

  def query(self,text=None):
    ''' answers queries based on model built by Trainer'''
    if not text: text = input("Query:")
    else: print("Query:", text)
    self.nlp_engine.from_text(text)
    X=[]
    for f, r, t, _ in self.nlp_engine.facts():
      X.append([f,r,t])
    X = np.array(X)

    hot_X = self.enc_X.transform(X).toarray()

    #print('@@@@',hot_X.shape)
    y=np.array(self.trainer.classifier.predict(hot_X))
    print('!!!',y.shape)

    m=self.enc_y.inverse_transform(y)
    sids=m.flatten().tolist()
    sids=[x for x in sids  if x!=None]
    self.show_answers(sids)

def sktest() :
  i=Inferencer()
  print("\n\n")
  print("ALGORITHMICALLY DERIVED ANSWERS:\n")
  i.ask("What did about black holes?")
  i.ask(text="What was in Roger's 1965 paper?")
  print("\n")
  print("NEURAL NET'S ANSWERS:\n")
  i.query("What did Penrose show about black holes?")
  i.query(text="What was in Roger's 1965 paper?")

if __name__=="__main__" :
  sktest()
