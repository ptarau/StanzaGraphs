
import subprocess
import json

import langid

PARAMS=dict(
  TARGET_LANG='fr',
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
