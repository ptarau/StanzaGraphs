import numpy as np
import nltk
import torch

import sentence_transformers as st

def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))


LANG_MODEL = 'multi-qa-MiniLM-L6-cos-v1'

class UnivSims:
    """
    creates callable sentence encoder instance that
    given a list of sentences returns a 2D tensor of embeddings
    """

    def __init__(self, model_name=LANG_MODEL):
        self.device = 'gpu' if torch.cuda.is_available() else 'cpu'
        self.model = st.SentenceTransformer(model_name, device=self.device)

    def digest(self, text_or_sents):
        if isinstance(text_or_sents, str):
            sentences = nltk.sent_tokenize(text_or_sents)
        else:
            assert isinstance(text_or_sents, list)
            sentences = text_or_sents

        x = self.model.encode(
            sentences, show_progress_bar=False, convert_to_tensor=True, device=self.device
        )
        return sentences, x

    def similarity(self, emb1, emb2):
        return cosine(emb1, emb2)


def test_univsims():
    query = ["I had pizza and pasta."]

    text = """ 
    I ate dinner. 
    We had a three-course meal.
    Brad came to dinner with us.
    He loves fish tacos.
    In the end, we all felt like we ate too much.
    We all agreed; it was a magnificent evening.
    """

    B = UnivSims()
    _, embs1 = B.digest(text)
    _, embs2 = B.digest(query)
    for x in embs1:
        # print(len(x),'\n',x)
        for y in embs2:
            print('SIM:', B.similarity(x, y))


if __name__ == "__main__":
    test_univsims()

"""
SIM: 0.7547023
SIM: 0.70152575
SIM: 0.37438127
SIM: 0.18140553
SIM: 0.39911166
SIM: 0.34462675


"""
