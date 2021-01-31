import streamlit as st
from summarizer import *

st.title('StanzaGraphs ')



mes='''
a Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering System using TextGraphs and Neural Networks
'''

st.sidebar.write(mes)

lang=st.sidebar.selectbox('Language?',('English','Chinese'))

if lang=='English':
  lang='en'
  fname='texts/english'
else:
  lang='zh-hans'
  fname = 'texts/chinese'

proceed = st.sidebar.button('Run with selected options!')

def work(fname='texts/english',lang='en',wk=8, sk=5):
  st.write('WORKING ON:',fname)
  nlp = NLP(lang)
  nlp.from_file(fname)
  kws, sents, picg = nlp.info(wk, sk)
  st.write("\nSUMMARY:")
  for sent in sents: st.write(sent)

  st.sidebar.write("\nKEYWORDS:")
  for w in kws: st.sidebar.write(w)
  #gshow(picg, file_name='pics/' + self.fname + '.gv')

if proceed :
  work(fname=fname,lang=lang)
