import streamlit as st
from googletrans import Translator
from summarizer import *
import os


UPLOAD_DIRECTORY = "uploads"

st.sidebar.title('StanzaGraphs')
msg = '''A Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering \
    System using TextGraphs and Neural Networks'''
st.sidebar.write(msg)

lang=st.sidebar.selectbox('To Language?',('English','Chinese', 'russian','spanish' ))
#googletrans.LANGUAGES 
if lang=='English':
  lang='en'
  #fname='texts/english'
elif lang=='Chinese':
  lang='zh-cn'
  #fname = 'texts/chinese'
elif lang == 'russian':
  lang = 'ru'
elif lang == 'spanish':
  lang = 'es'

#proceed = st.sidebar.button('Run with selected options!')

'''
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

  st.sidebar.write("\nKEYWORDS:")
  #print("\nKEYWORDS:")

  #for w in kws: st.sidebar.write(w)
  for w in kws:
    result= translator.translate(w, dest=lang)
    #print(result.text,end='; ')
    st.sidebar.write(result.text)
  #gshow(picg, file_name='pics/' + self.fname + '.gv')

#if proceed :
  #work(fname=fname,lang=lang)
'''


def main():

    uploaded_file = st.sidebar.file_uploader('Select a File', type=['txt', 'pdf'])


    if uploaded_file is not None:
        print(f"New file uploaded: {uploaded_file.name}")

        fpath = save_uploaded_file(uploaded_file)

        st.sidebar.write(f'Language: {lang}')

        fname = fpath[:-4]
        print("fname: ") 
        print(fname)

        action = st.sidebar.selectbox("Choose an action", ["Summarize", "Ask a question"])
        if action == "Summarize":
            st.write('WORKING ON:',fname)
            #print('WORKING ON:',fname)
            nlp=NLP()
            nlp.from_file(fname)
            kws, sents, picg = nlp.info()
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
            pass
        #elif action == "Ask a question":
            #answerer(talker, lang)
    else:
        st.info("Please select a text file to upload")

'''
def summarizer(talker):
    notice = st.empty()
    notice.empty()
    st.header("Summary")
    st.write('\n\n'.join(talker.show_summary()))
    st.header("Keywords")
    st.write(', '.join(talker.get_keys()))

    '''


'''
def answerer(talker, lang):
    notice = st.empty()
    notice.info("Analyzing text")
    notice.empty()
    question = st.text_input("Enter a question")
    if question:
        long_answers, short_answer = interact(question, talker)
        if lang == 'en':
            st.write(f"Long Answer:\n" + '\n\n'.join(long_answers))
            st.write(f"Short Answer: " + short_answer[:short_answer.rfind(',')])
        else:
            st.write('\n\n'.join(long_answers))

'''
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
