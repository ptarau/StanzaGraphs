import streamlit as st

st.set_page_config(layout="wide")

st.title('StanzaGraph: Multilingual Summary and Keyword Extractor and Question-Answering System')

col1, col2 = st.beta_columns(2)



with col1:
    s1=0
    with st.form('Form1'):
        st.selectbox('Select flavor', ['Vanilla', 'Chocolate'])

        submitted1 = st.form_submit_button('Submit 1')
        if submitted1:
          s1 += 1
          st.write('SUBMITTED!',s1)

with col2:
    s2=0
    with st.form('Form2'):
        st.selectbox('Select Topping', ['Almonds', 'Sprinkles'])
        res=st.text_input('Movie title', 'Life of Brian')
        st.write(res+" "+res)

        submitted2 = st.form_submit_button('Submit 2')
        if submitted2 :
          s2+=1
          st.write('SUBMITTED!',s2)

state=0

st.sidebar.write('hello')
go=st.sidebar.button('Summarize it!')

if go :
  state+=1
  st.sidebar.write('DONE',state)

