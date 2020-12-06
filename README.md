# StanzaGraphs is a Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering System using TextGraphs and Neural Networks


The file ````summarizer.py``` generates dependency graphs of the form

```<from, edge_label, to, sentence_number_in_which_it_occurs>```

as ```.tsv``` (tab separated) or ```.pro``` (Prolog) files.
Note that ```edge_labels``` are obtained by concatenating ```POS``` tags of the two nodes and the ```dependency_link``` label connecting them.

The file ```answerer.py``` encodes the tab separated outputs of ```summarizer.py```
into OneHotEncoded matrices, ready for use for machine learning tools.

A simple symbolic algorithm defines a baseline for answering question related to a given test document (in folder ```texts```) that has been processsed.

Before running, do:

pip3 install -U stanza

On the first run for a given language, a model (about 1GB) is downloaded,
that might take a bit on slower networks. Once downloaded it goes in the

$HOME/stanza_resources/

directory.

See more about stanza at:

https://github.com/stanfordnlp/stanza
