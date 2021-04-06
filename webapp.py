import streamlit as st
import os
from googletrans import Translator
from summarizer import *
UPLOAD_DIRECTORY = "uploads"

def main():
  st.sidebar.write('StanzaGraphs ')
  mes='''
  a Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering System using TextGraphs and Neural Networks
  '''

  st.sidebar.write(mes)

  lang=st.sidebar.selectbox('Translate to?',('English','Chinese', 'russian','spanish' ))
  #googletrans.LANGUAGES 
  if lang=='English':
    lang='en'
  elif lang=='Chinese':
    lang='zh-cn'
  elif lang == 'russian':
    lang = 'ru'
  elif lang == 'spanish':
    lang = 'es'

  uploaded_file = st.sidebar.file_uploader('Select a File', type=['txt', 'pdf'])
  title = None
  action = None

  if uploaded_file is not None:
    print(f"New file uploaded: {uploaded_file.name}")
    fpath = save_uploaded_file(uploaded_file)
    if fpath[-4:] == '.pdf':
      pdf2txt(fpath[:-4])    
    text = file2string(fpath[:-4] + '.txt')

    data_lang = langid.classify(text)[0]
    st.sidebar.write(f'Language: {data_lang}')

    fname = fpath[:-4]
    print("fname: ") 
    print(fname)

    if not title or title != uploaded_file.name:
      title = uploaded_file.name
      action = st.sidebar.selectbox("Choose an option", ["Summarize", "Ask a question"])
      proceed = st.sidebar.button('Run with selected option!')
      if proceed :
        if action == "Summarize":
          st.write('select Summarize, fname: ', fname, 'to lang:', lang)
          work(fname=fname,lang=lang)
          pass
        elif action == "Ask a question":
          st.write('Ask a question')
          #answerer(talker, lang)    
    else:
        st.info("Please select a text file to upload")
  
  
  
def ropen(f) :
  return open(f,'r',encoding='utf8')

def file2string(fname):
  with ropen(fname) as f:
    return f.read()

    
def work(fname='texts/english',lang='en',wk=8, sk=5):
  st.write('WORKING ON:',fname)
  #print('WORKING ON:',fname)
  nlp=NLP()
  nlp.from_file(fname)
  kws, sents, picg = nlp.info(wk, sk)
  st.write("\nSUMMARY:")
  #print("\nSUMMARY:")
  translator = Translator()
  #for sent in sents: st.write(sent)
  for sent in sents : 
    result= translator.translate(sent, dest=lang)
    #print(result.text)
    st.write(result.text)

  st.write("\nKEYWORDS:")
  #print("\nKEYWORDS:")

  #for w in kws: st.sidebar.write(w)
  for w in kws:
    result= translator.translate(w, dest=lang)
    #print(result.text,end='; ')
    st.write(result.text)
  #gshow(picg, file_name='pics/' + self.fname + '.gv')



def save_uploaded_file(uploaded_file, fname=None):
    if not fname:
        fname = uploaded_file.name
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    fpath = os.path.join(UPLOAD_DIRECTORY, fname)
    with open(fpath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return fpath


if __name__ == "__main__":
    main()