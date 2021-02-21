# StanzaGraphs is a Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering System using TextGraphs and Neural Networks


The file ```summarizer.py``` generates dependency graphs of the form

```<from, edge_label, to, sentence_number_in_which_it_occurs>```

as ```.tsv``` (tab separated) or ```.pro``` (Prolog) files.
Note that ```edge_labels``` are obtained by concatenating ```POS``` tags of the two nodes and the ```dependency_link``` label connecting them.

The file ```answerer.py``` encodes the tab separated outputs of ```summarizer.py```
into OneHotEncoded matrices, ready for use for machine learning tools as well as a simple question answering algorithm based on shared dependency edges with text graph of the sentences in the document. 

A simple tensorflow keras based neural network implements a Trainer and an Inferencer using these matrices in file ```tf_answerer.py```

A simple symbolic algorithm defines a baseline for answering questions related to a given text document (in folder ```texts```) that has been processsed. A simple keras-based neural network is also included for the same task.

A proof-of-concept **streamlit** Web application is in file ```webapp.py```. You can run it as shwon in the script: 

```webapp.sh```

##Setup

This project requires 64 bit python 3.8 

Before running, do:

```pip3 install -U stanza```

You will also need to install pdftotext. This can be installed via pip
or your package manager of choice

On the first run for a given language, a model (about 1GB) is downloaded,
that might take a bit on slower networks. Once downloaded it goes in your home directory, in the the folder:

```stanza_resources/ ```

Also make sure dependencies in ```requirements.txt``` are all installed.

See more about **Stanza** at:

https://github.com/stanfordnlp/stanza

Linux and Mac users should have no issues but Windows users may require extra steps:

* Installing pdftotext may require Microsoft Visual C++ Build Tools

* Make sure to run python un UTF-8 mode either
set the the environment variable ```PYTHONUTF8=1``` or use ```-Xutf8``` command line option.


