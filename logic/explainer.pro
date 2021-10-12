

% what can be inferre from the network structure
network_guessable(N):-
  tester_at(N,Y,_T,Ms),
  once((
    member(M,Ms),
    trainer_at(M,Y,_,_Ms)
  )).


testable(N):-tester_at(N,_Y,_T,_Ms).

testables(Count):-aggregate_all(count,N,testable(N),Count).

network_guessables(Count):-
  aggregate_all(count,N,network_guessable(N),Count).

network_guessable_ratio(R=GCount/TCount):-
  testables(TCount),
  network_guessables(GCount),
  R is GCount/TCount.

network_limits:-
  do((
    network_guessable_ratio(Result),
    writeln((network_only->Result))
  )).

%%%%%%%%


content_guessable_with(Similarity-MinVal,N):-
   select_diverse_peers(Peers),
   tester_at(N,Y,T,_),
   once((
     member(M,Peers),
     trainer_at(M,Y,OtherT,_),
     call(Similarity,T,OtherT,Sim),
     %writeln(Similarity=Sim),
     Sim>MinVal
   )).

content_guessables_with(Similarity,Count):-
  aggregate_all(count,N,content_guessable_with(Similarity,N),Count).

content_guessable_ratio(Similarity,GCount/TCount=R):-
  testables(TCount),
  content_guessables_with(Similarity,GCount),
  R is GCount/TCount.


count_with(Label,Count,Old):-
   trainer_at(Old,Label,_,_),
   aggregate(count,cited_with(Label,Old),Count).


cited_with(Label,Old):-
  trainer_at(_New,Label,_,Ns),
  member(Old,Ns).

a_similarity(Name-Val):-is_similarity(Name,Val).

% not very useful - as in theory sky is the limit here
% excpt that in practice, it is not :-)
content_limits:-
  do((
    a_similarity(Similarity),
    content_guessable_ratio(Similarity,Result),
    writeln((Similarity->Result))
  )).

% computes limits on what can be achieved
% based on info about the network's structure
% or the content attached to its nodes
limits:-
  network_limits,
  content_limits.

