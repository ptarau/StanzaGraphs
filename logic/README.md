# A Symbolic Algorithm for the OGB arxiv node propery prediction dataset

Load the Prolog equivalent of the dataset from http://www.cse.unt.edu/~tarau/datasets/arxiv_all.pro.zip.

## How it works

Create a subdirectory called OUTPUT_DATA, unzip it and place in there.

To run the progam with SWI-Prolog, assumed to be in your path as ``swipl`` just type ``go.sh`` and then ``?-go.`` at the Prolog prompt.

The intersting code is in ``thinker.pro``. It uses similarity relations defined in ``sims.pro`` and some insight on why it works and its limitations can be explored with code in ``explainer.pro``.

Enjoy,
Paul Tarau

October, 2021
