import os
import subprocess

def ropen(f) :
  return open(f,'r',encoding='utf8')

def pdf2txt(pdf,txt):
  '''
  linux: yum install -y poppler-utils
  '''
  subprocess.run(["pdftotext", "-q",pdf,txt])

# read a file into a string text
def file2text(fname):
  with ropen(fname) as f:
    return f.read()    

def text2file(text,fname) :
  with open(fname,'w') as g:
    g.write(text)

def exists_file(fname) :
  ''' if it exists as file or dir'''
  return os.path.exists(fname)

def home_dir() :
  from pathlib import Path
  return str(Path.home())

def ensure_path(fname) :
  folder,_=os.path.split(fname)
  os.makedirs(folder, exist_ok=True)








