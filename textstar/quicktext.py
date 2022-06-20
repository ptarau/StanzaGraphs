from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

class W:
    def __init__(self, lemma, word, tag, i):
        self.lemma = lemma
        self.word = word
        self.tag = tag
        self.i = i

    def __repr__(self):
        return \
            f"W('{self.lemma}','{self.word}','{self.tag}',{self.i})"

def text2sents(text):
    lemmatizer = WordNetLemmatizer()
    sents = sent_tokenize(text)
    lss = []
    for sent in sents:
        ws = word_tokenize(sent)

        wts = pos_tag(ws)

        ls = []
        for i, (w, t) in enumerate(wts):
            tag = t[0]
            if i==0 and tag!='N': w=w.lower()
            if not w.isalpha(): continue
            lemma = lemmatizer.lemmatize(w)
            if tag not in "NVJR": continue
            ls.append(W(lemma, w, tag, i))
        if not ls: continue
        lss.append((ls, sent))
    return lss


def file2string(fname):
    with open(fname, 'r') as f:
        return f.read()


def test_quicktext():
    text = file2string('../texts/short.txt')
    lss = text2sents(text)
    for ls, s in lss:
        print(s)
        for w in ls:
            print(w)
        print()


if __name__ == "__main__":
    test_quicktext()
