import streamlit as st

from answerer import Query
from params import *
from summarizer import Summarizer
from translator import translate
from walker import clean_text_file

st.set_page_config(layout="wide")

st.title('StanzaGraph: Multilingual Summary and Keyword Extractor and Question-Answering System')

left, right = st.columns((1, 1))

uploaded_file = st.sidebar.file_uploader('Select a File', type=['txt', 'pdf'])


def handle_uploaded():
    if uploaded_file is None: return None
    fpath = save_uploaded_file()
    suf = fpath[-4:]
    fname = fpath[:-4]
    if suf == '.pdf':
        pname = fname + ".pdf"
        tname = fname + ".txt"
        if pdf2txt(pname, tname) :
            clean_text_file(tname)
            return fname
        else:
            with right:
                st.write('Conversion to text file failed!')
    elif suf == '.txt':
        return fname
    else:
        with right:
            st.write('Please upload a .txt or a .pdf file!')


def save_uploaded_file():
    upload_dir = PARAMS['UPLOAD_DIRECTORY']
    fname = uploaded_file.name
    fpath = os.path.join(upload_dir, fname)
    if exists_file(fpath): return fpath
    ensure_path(upload_dir)
    with open(fpath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return fpath


target_lang = st.sidebar.text_input('Language you are familiar with (as a 2 letter code):', 'en')
PARAMS['TARGET_LANG'] = target_lang

summarize = st.sidebar.button('Summarize it!')

with st.sidebar:
    with st.form('Query'):
        question = st.text_area(
            'Enter a question in your language here:',
            "")

        query = st.form_submit_button('Submit your question!')
        if query:
            with left:
                st.write('Question:' + " " + question)


def do_summary():
    fname = handle_uploaded()
    if not fname: st.write('Please upload a file!')

    nlp = Summarizer()
    nlp.from_file(fname)

    kws, _, sents, picg = nlp.info()
    with right:
        st.write("\nSUMMARY:")
        for sent in sents: st.write(sent)

        st.write("\nKEYWORDS:")
        # for w in kws: st.write(w)
        s = "; ".join(kws)
        st.write(s)
    # gshow(picg, file_name='pics/' + self.fname + '.gv')


def do_query():
    fname = handle_uploaded()
    if not fname:
        st.write('Please upload a file!')
        return
    q = Query(fname=fname)
    with left:
        st.write('Answers:')
        answers = list(q.get_answers(question))
        if not answers:
            st.write(translate("I do not know."))
        else:
            for (_, sent) in answers:
                st.write(sent)


if summarize:
    do_summary()
elif query:
    do_summary()
    do_query()
