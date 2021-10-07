mock_similarity(_A,_B,1).

% similarity based on shared small subtrees "termlets"
termlet_similarity(A,B,Sim):-
   param(max_termlet_size,MaxTS),
   aggregate_all(sum(Sim),sharing_count(MaxTS,A,B,Sim),Sim).

sharing_count(MaxTS,A,B,Res):-
  sub_term(T,A),
  term_size(T,Size0),
  Size is 1+Size0,
  Size=<MaxTS,
  occurrences_of_term(T,B,Count),
  Count>0,
  Res is Size*Count.

% similarity based on co-paths in the two terms

list_path_similarity(A,B,Sim):-
  path_aggregator(list_path_weight,A,B, Sim).

set_path_similarity(A,B,Sim):-
  path_aggregator(set_path_weight,A,B, Sim).


path_aggregator(F,A,B, Sim):-
   param(path_similarity_start,Depth),
   aggregate_all(count,call(F,Depth,A,B,_X),Sim).

path_aggregator_alt(F,A,B, Sim):-
   param(path_similarity_start,Depth),
   term_size(A,S1),term_size(B,S2),Size is 1+min(S1,S2),
   aggregate_all(sum(X),call(F,Depth,A,B,X),Weight),
   Sim is Weight/Size.

list_path_weight(Depth,A,B,Weight):-
   to_forest(Depth,A,B,S,T),
   list_co_path(S,T,Path),
   length(Path,Weight).

set_path_weight(Depth,A,B,Weight):-
   to_forest(Depth,A,B,S,T),
   set_co_path(S,T,Path),
   length(Path,Weight).

set_co_path(S,T,Set):-distinct(Set,(arg_path(S,T,Path),sort(Path,Set))).

list_co_path(S,T,Path):-arg_path(S,T,Path).

% shared paths in two terms

emit_atom(S,S)-->!,[S].
emit_atom(_,_)-->[].


to_forest(0,A,B,S,T):-!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(A),!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(B),!,S=A,T=B.
to_forest(D,A,B,S,T):-D>0,DD is D-1,
   arg(_,A,AA),arg(_,B,BB),
   to_forest(DD,AA,BB,S,T).

arg_path_similarity(A,B,Weight):-
  aggregate_all(sum(X),arg_path_weight(A,B,X),Sum),
  normalize(Sum,Weight).

arg_path_weight(A,B,Weight):-
   arg_path(A,B,Path),
   length(Path,Weight).

arg_path(S,T,Path):-distinct(Path,arg_path(S,T,Path,[])).

arg_path(S,T)-->{atomic(S),atomic(T)},!,emit_atom(S,T).
arg_path(S,T)-->{atomic(S),functor(T,F,_)},!,emit_atom(S,F).
arg_path(S,T)-->{atomic(T),functor(S,F,_)},!,emit_atom(T,F).
arg_path(S,T)-->
  {functor(S,F,_),functor(T,G,_)},
  emit_atom(F,G),
  {arg(_I,S,X),arg(_J,T,Y)},
  arg_path(X,Y).


% jaccard similarity between nodes

nodes_of(S,Xs):-aggregate_all(set(X),node_of(S,X),Xs).

node_of(T,R):-atomic(T),!,R=T.
node_of(T,R):-
   (
     functor(T,R,_)
   ; arg(_,T,A),
     node_of(A,R)
   ).

node_jaccard_similarity(A,B,Sim):-
   nodes_of(A,Xs),
   nodes_of(B,Ys),
   jaccard(Xs,Ys,Sim).

% jaccard similarity between edges

edge_of(_Depth,T,R):-atomic(T),!,R=(T-T).
edge_of(Depth,T,R):-Depth>0,Deeper is Depth-1,
   functor(T,X,_),
   arg(_,T,A),
   edge_of(Deeper,A,Y-Z),
   (R=X-Y,X\=Y;R=Y-Z,Y\=Z).

edges_of(S,Xs):-
   param(depth_for_edges,Depth),
   aggregate_all(set(X),distinct(X,edge_of(Depth,S,X)),Xs).

edge_jaccard_similarity(A,B,Sim):-
   edges_of(A,Xs),
   edges_of(B,Ys),
   jaccard(Xs,Ys,Sim).

% jaccard similarity

jaccard(Xs,Ys,Sim):-
   ord_intersection(Xs,Ys,Zs),
   ( Zs=[]->Sim=0.0
   ; length(Zs,Shared),
     length(Xs,L),
     length(Ys,R),
     Sim is Shared/(L+R-Shared)
   ).

logistic(X,R):-R is 1/(1+exp(-X)).

normalize(X,R):-R is (2/(1+exp(-X)))-1.

% test similarities

simtest:-
   A=f(a,g(b,p(h(c))),i(c)),
   B=f(e,g(q(h(e)),b),i),
   writeln('A'=A),
   writeln('B'=B),
   edges_of(A,Xs),
   edges_of(B,Ys),
   ord_intersection(Xs,Ys,Zs),
   ord_union(Xs,Ys,Us),
   writeln(Zs),
   writeln(Us),
   node_jaccard_similarity(A,B,Sim0),
   writeln(node_jaccard=Sim0),
   edge_jaccard_similarity(A,B,Sim1),
   writeln(edge_jaccard=Sim1),
   termlet_similarity(A,B,Sim2),
   writeln(termlet=Sim2),
   set_path_similarity(A,B,Sim3),
   writeln(set_path=Sim3),
   set_path_similarity(A,B,Sim4),
   writeln(list_path=Sim4),
   forall(list_co_path(A,B,Path),writeln(Path)),
   fail
   ;
   writeln(done).
