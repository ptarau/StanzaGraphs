import streamlit as st
from summarizer import *
from answerer import *
import csv
import os


def main():
    SUPPORTED_LANGUAGES = get_supported_langs('StanzaSupportedLanguages.csv')
    st.sidebar.title('StanzaGraphs')
    msg = '''A Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering \
    System using TextGraphs and Neural Networks'''
    st.sidebar.write(msg)
    text_file = st.sidebar.file_uploader('Select a File', type=['txt'])
    selected_lang = st.sidebar.selectbox('Language', tuple(SUPPORTED_LANGUAGES.keys()), index=17)
    lang = SUPPORTED_LANGUAGES[selected_lang]

    action = st.sidebar.selectbox("Choose an action", ["Summarize", "Ask a question"])
    if text_file is not None:
        text = text_file.getvalue().decode("utf-8")
        if action == "Summarize":
            summarizer(input_text=text, lang=lang)
        elif action == "Ask a question":
            answerer(uploaded_file=text_file, text=text, lang=lang)
    else:
        st.info("Please select a text file to upload and its language")


def get_supported_langs(fname):
    # returns dictionary supported languages. Key is language, and value is language code
    langs = {}
    with open(fname, 'r', newline='', encoding='utf-8') as f_langs:
        reader = csv.DictReader(f_langs)
        for row in reader:
            langs[row['Language']] = row['Language code']
    return langs


def summarizer(input_text, lang='en', wk=8, sk=5):
    notice = st.empty()
    notice.info("Analyzing text")
    nlp = NLP(lang)
    nlp.from_text(input_text)
    kws, sents, picg = nlp.info(wk, sk)
    st.header("\nSUMMARY")
    for sent in sents:
        st.write(sent)
    st.header("Keywords")
    st.write(', '.join(kws))
    # gshow(picg, file_name='pics/' + self.fname + '.gv')
    notice.empty()


def answerer(uploaded_file, text, lang='en'):
    notice = st.empty()
    notice.info("Analyzing text")
    fname = 'texts/' + os.path.splitext(uploaded_file.name)[0]
    query = Query(fname=fname, text=text, lang=lang)
    notice.empty()
    question = st.text_input("Enter a question")
    if question:
        for answer in query.ask(question):
            st.write('* ' + answer)


if __name__ == "__main__":
    main()