
import subprocess
import langid

PARAMS=dict(
  TARGET_LANG='fr',
  RANKER='betweenness',
  UPLOAD_DIRECTORY='uploads/',
  OUTPUT_DIRECTORY='out/',
  k_count=7,
  s_count=4,
  translation=True,
  pics=False
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
