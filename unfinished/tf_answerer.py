from answerer import Data,Query
from params import *
import summarizer as nlp
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import load_model

class Trainer(Data) :
  """
  simple keras neural network trainer and model builder
  """
  def __init__(self,fname='texts/english',activation='sigmoid'):
    nlp.ensure_path("out/")
    nlp.ensure_path("pics/")
    model_file="out/"+fname+"_model"
    if nlp.exists_file(model_file) : return
    super().__init__(fname=fname)
    model = keras.Sequential()
    model.add(layers.Dense(128, input_dim=self.hot_X.shape[1], activation=activation))
    #model.add(layers.Dropout(0.5))
    model.add(layers.Dense(128, input_dim=self.hot_X.shape[1], activation=activation))
    #model.add(layers.Dropout(0.5))
    model.add(layers.Dense(128, input_dim=self.hot_X.shape[1], activation=activation))
    #model.add(layers.Dropout(0.5))
    model.add(layers.Dense(128, input_dim=self.hot_X.shape[1], activation=activation))
    #model.add(layers.Dropout(0.5))
    model.add(layers.Dense(self.hot_y.shape[1], activation='sigmoid'))
    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    history = model.fit(self.hot_X, self.hot_y, epochs=100, batch_size=16)

    model.save(model_file) # to be loaded by Inferencer and used for QA

    # visualize and inform about accuracy and loss
    plot_graphs("pics/"+fname + "_loss", history, 'loss')
    plot_graphs("pics/"+fname + "_acc", history, 'accuracy')

    loss, accuracy = model.evaluate(self.hot_X, self.hot_y)
    print('Accuracy:', round(100 * accuracy, 2), ', % Loss:', round(100 * loss, 2), '%')

class Inferencer(Query) :
  """
  loads model trained on associating dependency
  edges to sentences in which they occur
  """
  def __init__(self,fname='texts/english'):
    super().__init__(fname=fname)
    self.model = load_model("out/"+fname+"_model")

  def query(self,text=None):
    """ answers queries based on model built by Trainer"""
    if not text: text = input("Query:")
    else: print("Query:", text)
    self.nlp_engine.from_text(text)
    X=[]
    for f, ff, r, t, tt, _ in self.nlp_engine.facts():
      X.append([f,tt,r,tt,t])
    X = np.array(X)
    hot_X = self.enc_X.transform(X).toarray()
    y=self.model.predict(hot_X)
    ppp('@@@',y)
    m=self.enc_y.inverse_transform(y)
    sids=set(m.flatten().tolist())
    ppp('SENTECE IDS:',sids)
    self.show_answers(sids)

# VISUALS

import matplotlib.pyplot as plt

def plot_graphs(fname,history, metric):
  nlp.ensure_path(fname)
  plt.plot(history.history[metric])
  #plt.plot(history.history['val_'+metric], '')
  plt.xlabel("Epochs")
  plt.ylabel(metric)
  plt.legend([metric, 'val_'+metric])
  plt.savefig(fname + '.pdf',format="pdf",bbox_inches='tight')
  #plt.show()
  plt.close()

def ntest() :
  """ tests symbolic and neural QA on given document """
  t=Trainer()
  i=Inferencer()
  print("\n\n")
  print("ALGORITHMICALLY DERIVED ANSWERS:\n")
  i.ask("What did Penrose show about black holes?")
  i.ask(text="What was in Roger's 1965 paper?")
  print("\n")
  print("NEURAL NET'S ANSWERS:\n")
  i.query("What did Penrose show about black holes?")
  i.query(text="What was in Roger's 1965 paper?")

if __name__=="__main__" :
  ntest()
