from graphviz import Digraph as DotGraph

MAX_EDGES=2000

def gshow(g, attr=None, file_name='pics/temp.gv',view=False):
  if g is None: return

  ''' shows a networx DiGraph g
      using graphviz
      it could become slow on large graphs (above MAX_EDGES)
  '''
  ecount = g.number_of_edges()
  if ecount>MAX_EDGES:
    print('GRAPH TOO BIG TO SHOW, EDGES=', ecount)
    return
  dot = DotGraph()
  for e in gen_dot_edges(g,attr=attr):
    f, t, w = e
    dot.edge(f, t, label=w)
  print('generated:', file_name, 'edges:', ecount)
  dot.render(file_name, view=view)

def gen_dot_edges(g,attr=None) :
  for e in g.edges():
    f, t = e
    if not attr : w= ''
    else :
      w = g[f][t].get(attr)
      if not w : w=''
    if not isinstance(f,str) : f="#"+str(f)
    if not isinstance(t,str) : t="#"+str(t)
    f= f.replace(':','.')
    t = t.replace(':', '.')
    w=str(w)
    yield (f,t,w)

def xshow(gs, attr=None, file_name='pics/temp.gv',view=False):
  ''' shows a sequence of (possibly originating from the same,
     via a transformation) displayed together, left to right
  '''
  dot = DotGraph()
  ecount=0
  for i,g in enumerate(gs):
    k=g.number_of_edges()
    ecount+=k
    if ecount>MAX_EDGES :
      print('GRAPH CHAIN TOO BIG TO SHOW, EDGES=', ecount)
      return
    for f,t,w in gen_dot_edges(g,attr=attr) :
      mark="@"+str(i)
      dot.edge(f+mark, t+mark, label=w)
  print('generated:', file_name,'edges:',ecount)
  dot.render(file_name, view=view)
