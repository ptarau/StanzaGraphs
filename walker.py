import glob
import subprocess
from summarizer import exists_file, ensure_path, NLP
from nltk.tokenize import sent_tokenize, word_tokenize

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
  #print('cleaning: '+fname)
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
  for filename in sorted(glob.iglob(dir + '**/**', recursive=True)):
     yield filename

def  summarize_all(
    pdfs="pdfs/",
    overview="out/overview.txt",
    texts="out/pdftexts/",
    sums="out/sums/",
    keys="out/keys/",
    lang='en',
    wk=8,
    sk=4) :
  ensure_path(overview)
  with open(overview,'w') as outf :
    trim = len(pdfs)
    for pdf in walk(dir=pdfs):
      if pdf[-4:].lower() != ".pdf": continue

      name = pdf[trim:-4]

      tname0 = texts + name
      tname = texts + name + ".txt"
      sname = sums + name + ".txt"
      kname = keys + name + ".txt"

      ensure_path(tname)
      try :
        print('processing:', pdf)
        pdf2txt(pdf, tname)
        clean_text_file(tname, lang=lang)
        nlp = NLP(lang=lang)
        nlp.from_file(tname0)
        kws, sents, _ = nlp.info(wk, sk)

        ktext = "\n".join(kws)
        ensure_path(kname)
        string2file(ktext,kname)

        stext = "\n".join(sents)
        ensure_path(sname)
        string2file(stext,sname)

        text = "\n".join(
          ['FILE:', pdf, '\nKEYWORDS:', ktext, '\nSUMMARY:', stext, '\n'])
        print(text,file=outf)
      except :
        print('processing failed on:', pdf)




if __name__=="__main__":
  summarize_all()
  #for x in walk() : print(x)
