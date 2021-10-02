mock_similarity(_A,_B,4).

% based on shared paths
slow_path_similarity(A,B,Sim):-
   aggregate_all(max(Sim),shared_path_length(A,B,Sim),max(Sim)).

term_path(T,Ps):-distinct(Ps,term_path(T,Ps,[])).

term_path(T)-->{atomic(T)},[T].
term_path(T)-->{compound(T)},
  {functor(T,F,_)},
  [F],
  {arg(_,T,X)},
  term_path(X).

% based on shared subtrees
subtree_similarity(A,B,Sim):-
   aggregate_all(sum(Sim),sharing_count(A,B,Sim),Sim).

sharing_count(A,B,Res):-
  sub_term(T,A),
  occurrences_of_term(T,B,Count),
  Count>0,
  term_size(T,Size),
  Res is (1+Size)*Count.

shared_path_length(A,B,Sim):-
   term_path(A,Ps),
   term_path(B,Qs),
   intersection(Ps,Qs,Is),
   length(Is,Sim).

