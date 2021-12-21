import json
import os
import pickle
import subprocess
from inspect import getframeinfo, stack
from timeit import default_timer as timer

import langid

PARAMS = dict(
    TRACE=1,
    SEED=1234,
    MINSIM=3, # only edges with MINSIM * avg similarity are kept
    TARGET_LANG='en',  # tried zh,fr,sp,de,hu,ro,ar,el,la,it,ru,ja
    #RANKER='betweenness',
    RANKER='pagerank',
    UPLOAD_DIRECTORY='uploads/',
    OUTPUT_DIRECTORY='out/',
    k_count=8,
    s_count=5,
    trim=80,
    translation=True,
    pics=False,
    CACHING=0
)


def out_dirs():
    out = PARAMS['OUTPUT_DIRECTORY']
    return [out + x for x in
            ('overview.txt',
             'pdftexts/',
             'sums/',
             'keys/'
             )
            ]


def pdf2txt(pdf, txt):
    subprocess.run(["pdftotext", "-q", pdf, txt])
    if os.path.getsize(txt) > 32:
        return True
    os.remove(txt)
    return False


def detect_lang(text):
    return langid.classify(text)[0]


def to_json(obj, fname, indent=1):
    """
    serializes an object to a json file
    assumes object made of array and dicts
    """
    with open(fname, "w") as outf:
        # encode('utf8')
        json.dump(obj, outf, indent=indent, ensure_ascii=False)


def from_json(fname):
    """
    deserializes an object from a json file
    """
    with open(fname, "r") as inf:
        obj = json.load(inf)
        return obj


def exists_file(fname):
    """ if it exists as file or dir"""
    return os.path.exists(fname)


def home_dir():
    from pathlib import Path
    return str(Path.home())


def ensure_path(fname):
    folder, _ = os.path.split(fname)
    os.makedirs(folder, exist_ok=True)


def to_pickle(obj, fname='./arxiv.pickle'):
    """
    serializes an object to a .pickle file
    """
    ensure_path(fname)
    with open(fname, "wb") as outf:
        pickle.dump(obj, outf)


def from_pickle(fname):
    """
    deserializes an object from a pickle file
    """
    with open(fname, "rb") as inf:
        return pickle.load(inf)


def load_delimited(fname, delimiter):
    with open(fname, mode="rt") as f:
        for line in f:
            xs = line.split(delimiter)
            last = xs[-1]
            xs[-1] = last[0:-1]
            yield xs

def take(n, gen):
    for i, x in enumerate(gen):
        if i >= n: break
        yield x


def pp(gen, n=10):
    if isinstance(gen, dict):
        gen = gen.items()
    for x in take(n, gen):
        print(x)


def ppp(*args, **kwargs):
    """
    logging mechanism with possible DEBUG extras
    will tell from which line in which file the printed
    messge orginates from
    """
    if PARAMS["TRACE"] < 1: return
    if PARAMS["TRACE"] >= 1:
        caller = getframeinfo(stack()[1][0])
        print('DEBUG:',
              caller.filename.split('/')[-1],
              '->', caller.lineno, end=': ')
    print(*args, **kwargs)


"""
def force_quiet(fun,*args,**kwargs) :
  sout=sys.stdout
  serr = sys.stderr
  f = open(os.devnull, 'w')
  sys.stdout = f
  sys.stderr = f
  result=fun(*args,**kwargs)
  sys.stdout = sout
  sys.stderr = serr
  return result
"""
