import numpy as np
from sklearn.ensemble import RandomForestClassifier

from answerer import Query
from params import *


class Trainer:
    def __init__(self, hot_X, hot_y):
        self.classifier = RandomForestClassifier(n_estimators=100, n_jobs=16)
        self.classifier.fit(hot_X, hot_y)


from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class ScaledTrainer:
    def __init__(self, hot_X, hot_y):
        net = RandomForestClassifier(n_estimators=100, n_jobs=16)
        pipe = Pipeline([
            ('scale', StandardScaler()),
            ('net', net),
        ])
        self.classifier = pipe

        self.classifier.fit(hot_X, hot_y)


class Inferencer(Query):
    """
    loads model trained on associating dependency
    edges to sentences in which they occur
    """

    def __init__(self, fname='texts/english'):
        super().__init__(fname=fname)
        self.trainer = self.make_trainer(self.hot_X, self.hot_y)

    def make_trainer(self, X, y):
        return ScaledTrainer(X, y)

    def query(self, text=None):
        """ answers queries based on model built by Trainer"""
        if not text:
            text = input("Query: ")
        else:
            print("Query:", text)
        self.nlp_engine.from_text(text)
        X = []
        for f, ff, r, tt, t, _ in self.nlp_engine.facts():
            X.append([f, ff, r, tt, t])
        X = np.array(X)

        hot_X = self.enc_X.transform(X).toarray()

        # print('@@@@',hot_X.shape)
        y = np.array(self.trainer.classifier.predict(hot_X))
        ppp('!!!', y.shape, y)

        m = self.enc_y.inverse_transform(y)
        sids = m.flatten().tolist()
        sids = {x for x in sids if x != None}
        self.show_answers(sids)

    def interact(self):
        while True:
            text = input("Query: ")
            if not text: return
            self.query(text=text)


def sktest():
    i = Inferencer()
    print("\n\n")
    print("ALGORITHMICALLY DERIVED ANSWERS:\n")
    i.ask("What did Penrose prove about black holes?")
    i.ask(text="What was in Roger's 1965 paper?")
    print("\n")
    print("NEURAL NET'S ANSWERS:\n")
    i.query("What did Penrose show about black holes?")
    i.query(text="What was in Roger's 1965 paper?")


if __name__ == "__main__":
    sktest()
    # Inferencer().interact()
