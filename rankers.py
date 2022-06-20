import networkx as nx
from params import *

# alternative centrality algorithms

ranker_dict = dict()


def ranker(f):
    """
    decorator collecting selected rankers
    to  dictionary 'ranker_dict'
    """
    ranker_dict[f.__name__] = f
    return f


@ranker
def degrank(g):
    return nx.degree_centrality(g)


@ranker
def pagerank(g):
    return nx.pagerank(g)


@ranker
def closeness(g):
    return nx.closeness_centrality(g, distance="weight")


@ranker
def betweenness(g):
    return nx.betweenness_centrality(g, seed=PARAMS['SEED'], weight="weight")
