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

% similarity based on co-paths in the two terms

list_path_similarity(A,B,Sim):-
  path_aggregator(list_path_weight,A,B, Sim).

set_path_similarity(A,B,Sim):-
  path_aggregator(set_path_weight,A,B, Sim).

path_aggregator(F,A,B, Sim):-
   param(path_similarity_start,Depth),
   param(path_similarity_skip,Skip),
   term_size(A,S1),term_size(B,S2),Size is 1+min(S1,S2),
   aggregate_all(sum(X),call(F,Depth,Skip,A,B,X),Weight),
   Sim is Weight/Size.

list_path_weight(Depth,Skip,A,B,Weight):-
   to_forest(Depth,A,B,S,T),
   co_path(Skip,S,T,Path),
   length(Path,Weight).

set_path_weight(Depth,Skip,A,B,Weight):-
   to_forest(Depth,A,B,S,T),
   co_set_path(Skip,S,T,Path),
   length(Path,Weight).

co_set_path(Skip,S,T,Set):-distinct(Set,(co_path(Skip,S,T,Path,[]),sort(Path,Set))).

co_path(Skip,S,T,Path):-distinct(Path,co_path(Skip,S,T,Path,[])).

% shared paths in two terms

co_path(_,S,T)-->{atomic(S),atomic(T)},!,emit_atom(S,T).
co_path(_,S,T)-->{atomic(S),functor(T,F,_)},!,emit_atom(S,F).
co_path(_,S,T)-->{atomic(T),functor(S,F,_)},!,emit_atom(T,F).
co_path(Skip,S,T)-->
  {functor(S,F,_),functor(T,G,_)},
  maybe_skip(F,G,Skip,SkipLater),
  {arg(_,S,X),arg(_,T,Y)},
  co_path(SkipLater,X,Y).

emit_atom(S,S)-->!,[S].
emit_atom(_,_)-->[].

maybe_skip(F,F,Skip,Skip)-->!,[F].
maybe_skip(_F,_G,Skip,NewSkip)-->{Skip>0,NewSkip is Skip-1}.

to_forest(0,A,B,S,T):-!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(A),!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(B),!,S=A,T=B.
to_forest(D,A,B,S,T):-D>0,DD is D-1,
   arg(_,A,AA),arg(_,B,BB),
   to_forest(DD,AA,BB,S,T).


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
   subtree_similarity(A,B,Sim2),
   writeln(subtree=Sim2),
   set_path_similarity(A,B,Sim3),
   writeln(set_path=Sim3),
   set_path_similarity(A,B,Sim4),
   writeln(list_path=Sim4),
   forall(co_path(0,A,B,Path),writeln(Path)),
   fail
   ;
   writeln(done).
