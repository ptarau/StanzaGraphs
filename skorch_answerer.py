# NOT WORKING - multiple targets not enabled in skorch

import numpy as np
from sklearn.datasets import make_classification
from torch import nn
import torch.nn.functional as F
from answerer import Data

from skorch import NeuralNet, NeuralNetClassifier


def make_data() :
  data=Data()
  X=data.hot_X
  y=data.hot_y
  #return X,np.sum(y,axis=1)
  return X,y

X,y=make_data()


#X, y = make_classification(1000, 20, n_informative=10, random_state=0)
#print("X",X.shape,"y",y.shape)



X = X.astype(np.float32)
y = y.astype(np.int64)

print("X",X.shape,"y",y.shape)

class MyModule(nn.Module):
    def __init__(self, num_units=10, nonlin=F.relu):
        super(MyModule, self).__init__()

        self.dense0 = nn.Linear(X.shape[1], num_units)
        self.nonlin = nonlin
        self.dropout = nn.Dropout(0.5)
        self.dense1 = nn.Linear(num_units, 10)
        self.output = nn.Linear(10, 2)

    def forward(self, X, **kwargs):
        X = self.nonlin(self.dense0(X))
        X = self.dropout(X)
        X = F.relu(self.dense1(X))
        X = F.softmax(self.output(X))
        return X

net = NeuralNet(
    MyModule,
    nn.CrossEntropyLoss,
    #nn.MultiLabelMarginLoss,
    max_epochs=20,
    lr=0.1,
    #batch_size=514,
    # Shuffle training data on each epoch
    iterator_train__shuffle=True,
)

def train(X,y) :
  #net.fit(X, y[:,7])
  net.fit(X, np.min(y,axis=1))
  y_proba = net.predict_proba(X)
  for x in y_proba : print(x)


if __name__=="__main__" :
  train(X,y)
