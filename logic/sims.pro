mock_similarity(_A,_B,1).

% similarity based on shared subtrees
subtree_similarity(A,B,Sim):-
   aggregate_all(sum(Sim),sharing_count(A,B,Sim),Sim).

sharing_count(A,B,Res):-
  sub_term(T,A),
  occurrences_of_term(T,B,Count),
  Count>0,
  term_size(T,Size),
  Res is (1+Size)*Count.

% based on shared paths
slow_path_similarity(A,B,Sim):-
   aggregate_all(max(Sim),shared_path_length(A,B,Sim),Sim).

term_path(T,Ps):-distinct(Ps,term_path(T,Ps,[])).

term_path(T)-->{atomic(T)},[T].
term_path(T)-->{compound(T)},
  {functor(T,F,_)},
  [F],
  {arg(_,T,X)},
  term_path(X).

shared_path_length(A,B,Sim):-
   term_path(A,Ps),
   term_path(B,Qs),
   intersection(Ps,Qs,Is),
   length(Is,Sim).

% similarity based on co-paths in the two terms

fast_path_similarity(A,B,Sim):-
  %term_size(A,S1),term_size(B,S2),writeln(sizes(S1,S2)),
  aggregate_all(max(X),co_path_length(A,B,X),Sim).

to_forest(0,A,B,S,T):-!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(A),!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(B),!,S=A,T=B.
to_forest(D,A,B,S,T):-D>0,DD is D-1,
   arg(_,A,AA),arg(_,B,BB),
   to_forest(DD,AA,BB,S,T).

co_path_length(A,B,Len):-
   param(path_similarity_start,Depth),
   to_forest(Depth,A,B,S,T),
   co_path(S,T,Ps),
   length(Ps,Len).

co_path(S,T,Ps):-co_path(3,S,T,Ps).

co_path(Skip,S,T,Ps):-distinct(Ps,co_path(Skip,S,T,Ps,[])).

co_path(_,S,_)-->{atomic(S)},!.
co_path(_,_,T)-->{atomic(T)},!.
co_path(Skip,S,T)-->
  {functor(S,F,_),functor(T,G,_)},
  maybe_skip(F,G,Skip,SkipLater),
  {arg(_,S,X),arg(_,T,Y)},
  co_path(SkipLater,X,Y).

maybe_skip(F,F,Skip,Skip)-->!,[F].
maybe_skip(_F,_G,Skip,NewSkip)-->{Skip>0,NewSkip is Skip-1}.

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

% test similarities

simtest:-
   A=f(a,g(b,p(h(c))),i(c)),
   B=f(e,g(q(h(e)),b),i),
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
   subtree_similarity(A,B,Sim2),
   writeln(subtree=Sim2),
   slow_path_similarity(A,B,Sim3),
   writeln(slow_path=Sim3),
   fast_path_similarity(A,B,Sim4),
   writeln(fast_path=Sim4),
   fail
   ;
   writeln(done).
