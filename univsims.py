import numpy as np
import tensorflow_hub as hub
import nltk

def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))


class UnivSims:
    def __init__(self):
        module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        #module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
        self.model = hub.load(module_url)

    def digest(self,text_or_sents):
        if isinstance(text_or_sents,str) :
           sentences = nltk.sent_tokenize(text_or_sents)
        else:
           assert isinstance(text_or_sents,list)
           sentences=text_or_sents
        sentence_embeddings = self.model(sentences)
        return sentences, sentence_embeddings

    def similarity(self, emb1, emb2):
        return cosine(emb1,emb2)


def test_univsims():
    query = ["The color of the sky is blue."]

    text = """ 
    I just had breakfest.
    Clouds are usually white.
    What is your name?
    What color is the sky?
    """

    B = UnivSims()
    _, embs1 = B.digest(text)
    _, embs2 = B.digest(query)
    for x in embs1:
        #print(len(x),'\n',x)
        for y in embs2:
           print('SIM:',B.similarity(x,y))


if __name__ == "__main__":
    test_univsims()
