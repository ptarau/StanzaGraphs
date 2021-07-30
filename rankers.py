import networkx as nx

# alternative centrality algorithms

ranker_dict=dict()

def ranker(f) :
  """
  decorator collecting selected rankers
  to  dictionary 'ranker_dict'
  """
  ranker_dict[f.__name__]=f
  return f

@ranker
def pagerank(g) :
  return nx.pagerank(g)

@ranker
def subg(g) :
  if g.is_directed(): g=g.to_undirected()
  return nx.subgraph_centrality(g)

@ranker
def closeness(g) :
  return nx.closeness_centrality(g,distance="weight")

@ranker
def betweenness(g) :
  return nx.betweenness_centrality(g,weight="weight")
