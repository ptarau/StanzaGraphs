% todo

network_guessable(N):-
  at(N,te,Y,_T,Ms),
  once((
    member(M,Ms),
    at(M,Kind,Y,_,_Ms),
    member(Kind,[va,tr])
  )).


testable(N):-at(N,te,_Y,_T,_Ms).

testables(Count):-aggregate_all(count,N,testable(N),Count).

network_guessables(Count):-
  aggregate_all(count,N,network_guessable(N),Count).

network_guessable_ratio(R):-
  testables(TCount),
  network_guessables(GCount),
  R is GCount/TCount.

nlp_guessable_with(Similarity,N):-
   at(N,te,Y,T,_),
   once((
     at(_M,Kind,Y,OtherT,_),
     member(Kind,[va,tr]),
     call(Similarity,T,OtherT,Sim),
     Sim>0
   )).

nlp_guessables_with(Similarity,Count):-
  aggregate_all(count,N,nlp_guessable_with(Similarity,N),Count).

nlp_guessable_ratio(Similarity,R):-
  testables(TCount),
  nlp_guessables_with(Similarity,GCount),
  R is GCount/TCount.
