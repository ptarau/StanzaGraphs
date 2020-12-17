import glob
import subprocess
from summarizer import exists_file, ensure_path, NLP

def pdf2txt(pdf,txt):
  subprocess.run(["pdftotext", "-q",pdf,txt])

def file2string(fname):
  with open(fname,'r') as f:
    return f.read()

def string2file(text,fname) :
  with open(fname,'w') as g:
    g.write(text)

def clean_text_file(fname,lang='en') :
  if lang!='en': return
  print('cleaning: '+fname)
  from nltk.tokenize import sent_tokenize, word_tokenize
  data = file2string(fname)
  texts=sent_tokenize(data)
  clean=[]
  for text in texts :
    ws=word_tokenize(text)
    good=0
    bad=0
    if len(ws)>256 : continue
    for w in ws :
      if w.isalpha() and len(w)>1 :good+=1
      else : bad+=1
    if good/(1+bad+good) <0.75 : continue
    if ws[-1] not in ".?!" : ws.append(".")
    sent=" ".join(ws)
    clean.append(sent)
  new_data="\n".join(clean)
  string2file(new_data,fname)

def walk(dir="./"):
  for filename in glob.iglob(dir + '**/**', recursive=True):
     yield filename

def  summarize_all(
    pdfs="pdfs/",
    texts="out/pdftexts/",
    sums="out/sums/",
    keys="out/keys/",
    lang='en',
    wk=8,
    sk=4) :
  trim=len(pdfs)
  for pdf in walk(dir=pdfs) :
    if pdf[-4:].lower()!=".pdf" : continue

    name=pdf[trim:-4]

    tname0 = texts + name
    tname=texts+name+".txt"
    sname = sums + name + ".txt"
    kname = keys + name +".txt"

    ensure_path(tname)
    pdf2txt(pdf,tname)
    print('processing:',tname)
    clean_text_file(tname,lang=lang)
    nlp=NLP(lang=lang)
    nlp.from_file(tname0)
    kws,sents,_=nlp.info(wk,sk)
    print('KEYWORDS',kws)
    print('')
    print('SUMMARY',sents)
    print('')

if __name__=="__main__":
  summarize_all()
