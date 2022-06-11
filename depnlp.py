import stanza
from collections import defaultdict
from zss import simple_distance, Node
from nltk.tokenize import word_tokenize
from collections import Counter

from params import *


class DepBuilder:
    def __init__(self, lang='en', source='text'):
        self.out = PARAMS['OUTPUT_DIRECTORY']
        ensure_path(self.out)
        if not exists_file(home_dir() + '/stanza_resources/' + lang):
            stanza.download(lang)

        kwargs = dict(lang=lang, logging_level='ERROR')

        if source in {'text', 'file'}:
            kwargs['processors'] = 'tokenize,lemma,pos,depparse'
        elif source in {'sentences', 'tokens'}:
            kwargs['processors'] = 'tokenize,lemma,pos,depparse'
            kwargs['tokenize_pretokenized'] = True
        else:
            raise "wrong source"
        self.nlp = stanza.Pipeline(**kwargs)

    # process text from a file
    def from_file(self, fname=None):
        self.fname = fname
        text = file2text(fname + ".txt")
        self.fact_list = None
        self.doc = self.nlp(text)
        # print('LANGUAGE:',self.lang)

    def from_text(self, text="Hello!"):
        self.fact_list = None
        self.doc = self.nlp(text)

    def from_sentences(self, sents=None):
        self.fact_list = None
        wss = [word_tokenize(sent) for sent in sents]

        self.doc = self.nlp(wss)

    def from_tokenized(self, tokenized=None):
        self.fact_list = None
        self.doc = self.nlp(tokenized)

    def process_deps(self, facts=False):

        clauses = []

        def rule(x, sent, sid, clause):
            if x.head == 0:
                source = x.lemma, sid
                target = 'sent_', sid
                clause[target].append(source)
            elif x.upos == 'PUNCT':
                pass
            else:
                hw = sent.words[x.head - 1]
                target = hw.lemma, sid  # , hw.upos
                source = x.lemma, sid  # , x.upos
                clause[target].append(source)
                # x.lemma, x.upos, x.deprel, hw.upos, hw.lemma, sid

        for sid, sent in enumerate(self.doc.sentences):
            clause = defaultdict(list)
            for word in sent.words:
                rule(word, sent, sid, clause)
            clauses.append(clause)

            if not facts: continue

            clause = defaultdict(list)
            for x in sent.words:
                if x.upos != "PUNCT":
                    head = x.lemma, sid  # , x.upos
                    clause[head] = []
                    if clause not in clauses:
                        clauses.append(clause)

        self.clauses = clauses

    def to_zss(self):

        def transform(parent):
            if parent not in clause:
                return Node(parent[0])

            children = clause[parent]
            root = parent[0]
            xs = []
            for child in children:
                xs.append(transform(child))
            res = Node(root, children=xs)
            return res

        for sid, clause in enumerate(self.clauses):
            root = 'sent_', sid
            yield transform(root)

    def to_terms(self):

        def to_term(parent):
            if parent not in clause:
                return parent[0]

            children = clause[parent]
            res = [parent[0]]
            for child in children:
                res.append(to_term(child))
            return res

        for sid, clause in enumerate(self.clauses):
            root = 'sent_', sid
            yield to_term(root)

    def to_repr(self):
        def quote(s):
            s=str(s)
            if s and s[0].isupper() or s[0]=="_":
                s="'"+s+"'"
            return s

        def to_term(parent):
            if parent not in clause:
                return quote(parent[0])

            children = clause[parent]
            fun=quote(parent[0])+"("
            res=[]
            for child in children:
                res.append(to_term(child))
            s=",".join(res)
            return fun+s+")"

        for sid, clause in enumerate(self.clauses):
            root = 'sent_', sid
            yield to_term(root)

    def to_prolog(self, pfile):
        with open(pfile, 'w') as f:
            for t in self.to_repr():
                #print('term(', t, file=f, end=').\n')
                print("term("+t+").",file=f)

    def to_natprog(self):
        wss = []
        for clause in self.clauses:
            for h, bs in clause.items():
                ws = list(h)
                if bs == []:
                    ws.append('.')
                else:
                    ws.append(':')
                    for b in bs:
                        ws.extend(b)
                        ws.append(',')
                    ws[-1] = '.'
                ws = map(str, ws)
                wss.append(" ".join(ws))
        # wss= sorted(wss)
        return wss


def below(t):
    if not isinstance(t, list):
        return 1, t

    f = t[0]
    ts = t[1:]
    xs = [below(x) for x in ts]
    w = 1 + sum(wx for (wx, _) in xs)
    return w, [f] + xs


def betrank(t):
    bt = below(t)
    s, _ = bt

    ranks = Counter()

    def comp(ws):
        s = 0
        for i, wi in enumerate(ws):
            for j, wj in enumerate(ws):
                if i < j:
                    s += wi * wj
        return s

    def walk(t):
        w, fxs = t
        if not isinstance(fxs, list):
            leaf = 0, w, fxs
            ranks[fxs] += 0
            return leaf
        f = fxs[0]
        xs = fxs[1:]
        upper = s - w
        lowers = [walk(x) for x in xs]
        ws = [l for (_, l, _) in lowers]
        ws.append(upper)
        c = comp(ws)
        r = c, w, [f] + lowers
        ranks[f] += c
        return r

    return ranks, walk(bt)


def showranks(rs):
    print('RANKS:')
    for k, w in rs.most_common():
        if w == 0: break
        print(k, w)
    print()


def test_nlp(from_sents=True):
    if not from_sents:

        text = """
       Just days before the official start of the 2022 hurricane season, 
       Hurricane Agatha is barreling toward Mexico’s southwestern coast Monday, 
       forecasters at the National Hurricane Center said. 
       The storm is expected to make landfall in southern Mexico later today.
       It is believed that the hurricane will bring a lot of floading.
       """
        db = DepBuilder()
        db.from_text(text)
    else:
        sents = [
            "The cat sits on the mat.",
            "A feline sits on a surface.",
            "The bear sits on the grass.",
            "The penguin Tweety walks on the snow."
        ]

        db = DepBuilder(source='sentences')
        db.from_sentences(sents)

    db.process_deps()
    for x in db.to_natprog():
        print(x)
    print('')
    for x in db.to_terms():
        print(x)
    print('')
    zs = list(db.to_zss())
    for x in zs:
        print(x, '\n')
    print('')
    for i, x in enumerate(zs):
        for j, y in enumerate(zs):
            print('DIST:', [i, j], simple_distance(x, y))

    db.to_prolog('out/temp.pro')

    for x in db.to_terms():
        b = below(x)
        print('\nBELOW:', b)
        rs, _ = betrank(x)
        print('\nBETRANK:')
        showranks(rs)
    print('')

    t = ['a', ['b', ['c', ['d', 'e']], 'f'], 'g', 'h']
    print('\nBELOW AGAIN:\n', t, '\n', below(t))
    rs, _ = betrank(t)
    showranks(rs)


if __name__ == "__main__":
    test_nlp(from_sents=False)
    test_nlp(from_sents=True)
