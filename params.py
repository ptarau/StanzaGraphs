
import subprocess
import os
import json
from inspect import getframeinfo, stack

import langid

PARAMS=dict(
  TRACE=1,
  TARGET_LANG='en', # tried zh,fr,sp,de,hu,ro,ar,el,la,it,ru,ja
  RANKER='betweenness',
  UPLOAD_DIRECTORY='uploads/',
  OUTPUT_DIRECTORY='out/',
  k_count=7,
  s_count=4,
  translation=True,
  pics=False,
  CACHING=True
)

def out_dirs() :
  out=PARAMS['OUTPUT_DIRECTORY']
  return [out+x for x in
          ('overview.txt',
           'pdftexts/',
           'sums/',
           'keys/'
           )
          ]

def pdf2txt(pdf,txt):
  subprocess.run(["pdftotext", "-q",pdf,txt])
  if os.path.getsize(txt) > 32 :
    return True
  os.remove(txt)
  return False


def detect_lang(text):
  return langid.classify(text)[0]


def to_json(obj,fname,indent=1) :
  """
  serializes an object to a json file
  assumes object made of array and dicts
  """
  with open(fname, "w") as outf:
    #encode('utf8')
    json.dump(obj,outf,indent=indent,ensure_ascii = False)

def from_json(fname) :
  """
  deserializes an object from a json file
  """
  with open(fname, "r") as inf:
    obj = json.load(inf)
    return obj


def ppp(*args,**kwargs) :
  """
  logging mechanism with possible DEBUG extras
  will tell from which line in which file the printed
  messge orginates from
  """
  if PARAMS["TRACE"] < 1: return
  if PARAMS["TRACE"] >= 1 :
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
