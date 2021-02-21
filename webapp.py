import streamlit as st
from summarizer import *
import csv

st.title('StanzaGraphs ')

msg = '''
A Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering System using TextGraphs and Neural Networks
'''


def get_supported_langs(fname):
    # returns dictionary supported languages. Key is language, and value is language code
    langs = {}
    with open(fname, 'r', newline='', encoding='utf-8') as f_langs:
        reader = csv.DictReader(f_langs)
        for row in reader:
            langs[row['Language']] = row['Language code']
    return langs


notices = st.empty()
SUPPORTED_LANGUAGES = get_supported_langs('StanzaSupportedLanguages.csv')
st.sidebar.write(msg)

text_file = st.sidebar.file_uploader('Input File', type=['txt'])
selected_lang = st.sidebar.selectbox('Language', tuple(SUPPORTED_LANGUAGES.keys()), index=17)

lang = SUPPORTED_LANGUAGES[selected_lang]
proceed = st.sidebar.button('Analyze!')


def summarizer(input_text, lang='en', wk=8, sk=5):
    notices.info("Analyzing text")
    nlp = NLP(lang)
    nlp.from_text(input_text)
    kws, sents, picg = nlp.info(wk, sk)
    st.header("\nSUMMARY")
    for sent in sents:
        st.write(sent)
    st.header("Keywords")
    st.write(', '.join(kws))
    # gshow(picg, file_name='pics/' + self.fname + '.gv')
    notices.empty()


if proceed:
    if text_file is not None:
        text = text_file.getvalue().decode("utf-8")
        summarizer(text, lang=lang)
    else:
        st.error("Please select a file to analyze")

