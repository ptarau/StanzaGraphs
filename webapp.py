import streamlit as st
from myfile import * 
from googletrans import Translator, LANGCODES, LANGUAGES
from summarizer import *
from answerer import *

UPLOAD_DIRECTORY = "uploads"

def main():
  st.sidebar.write('StanzaGraphs ')
  mes='''
  a Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering System using TextGraphs and Neural Networks
  '''

  st.sidebar.write(mes)
  langList = ['', 'Select Language']
  langList +=  list(LANGCODES.keys())
  langFull=st.sidebar.selectbox('To Language?', langList)
  lang = LANGCODES.get(langFull)
  st.write('Selected language: ', langFull)

  uploaded_file = st.sidebar.file_uploader('Select a File', type=['txt', 'pdf'])
  title = None
  action = None

  if uploaded_file is not None:
    print(f"New file uploaded: {uploaded_file.name}")
    fpath = save_uploaded_file(uploaded_file)
    if fpath[-4:] == '.pdf':
      pdf2txt(fpath[:-4])    
    text = file2text(fpath[:-4] + '.txt')

    data_lang = langid.classify(text)[0]
    st.sidebar.write(f'Language: {data_lang}')

    fname = fpath[:-4]
    print("fname: ") 
    print(fname)

    if not title or title != uploaded_file.name:
      title = uploaded_file.name
      action = st.sidebar.selectbox("Choose an action", ["Summarize", "Ask a question"])     
      if action == "Summarize":
        proceed = st.sidebar.button('Run with selected option!')
        if proceed:
          st.write('Translate summary from ', fname, 'to ', langFull)
          summary(fname=fname,lang=lang)
          pass
      elif action == "Ask a question":
        st.write('Ask a question')        
        question = st.text_input('Input your question here:') 
        if question:          
          st.write('Answers:')
          answer(fname, question, lang)    
    else:
        st.info("Please select a text file to upload")
  
  
  
    
def summary(fname='texts/english',lang='en',wk=8, sk=5):
  st.write('WORKING ON:',fname)
  nlp=NLP()
  nlp.from_file(fname)
  kws, sents, picg = nlp.info(wk, sk)
  st.write("\n\nSUMMARY:")
  translator = Translator()
  for sent in sents : 
    result= translator.translate(sent, dest=lang)
    st.write(result.text)

  st.write("\n\nKEYWORDS:")
  for w in kws:
    result= translator.translate(w, dest=lang)
    st.write(result.text)


def answer(file_name, question, lang = 'en'):
  q = Query(file_name)
  q.ask(question, tolang = lang)
  if len(q.answer) == 0:
    st.write("No answers")
  else:
    for id in q.answer:
      st.write(id, ':', q.answer[id])


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