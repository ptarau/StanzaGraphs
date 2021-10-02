mock_similarity(_A,_B,4).

% based on shared subtrees
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

% based on co-paths in the two terms
fast_path_similarity(A,B,Sim):-
  %term_size(A,S1),term_size(B,S2),writeln(sizes(S1,S2)),
  aggregate_all(max(X),co_path_length(A,B,X),Sim0),
  %writeln(sim=Sim0),
  Sim is 2+Sim0.

to_forest(0,A,B,S,T):-!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(A),!,S=A,T=B.
to_forest(_,A,B,S,T):-atomic(B),!,S=A,T=B.
to_forest(D,A,B,S,T):-D>0,DD is D-1,
   arg(_,A,AA),arg(_,B,BB),
   to_forest(DD,AA,BB,S,T).

co_path_length(A,B,Len):-
   to_forest(2,A,B,S,T),
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

% jaccard_nodes_similarity

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

jaccard(Xs,Ys,Sim):-
   ord_intersection(Xs,Ys,Zs),
   ( Zs=[]->Sim=0.0
   ; length(Zs,Shared),
     length(Xs,L),
     length(Ys,R),
     Sim is Shared/(L+R-Shared)
   ).

edge_of(T,R):-atomic(T),!,R=(T-T).
edge_of(T,R):-
   functor(T,X,_),
   arg(_,T,A),
   edge_of(A,Y-Z),
   (R=X-Y,X\=Y;R=Y-Z,Y\=Z).

edges_of(S,Xs):-aggregate_all(set(X),edge_of(S,X),Xs).

edge_jaccard_similarity(A,B,Sim):-
   edges_of(A,Xs),
   edges_of(B,Ys),
   jaccard(Xs,Ys,Sim).

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
