% todo

% guessing the closest with several similarities

guess:-
   %guess([tr,va]),
   guess([te]).

guess(Kinds):-
  count_nodes(Kinds,Total),
  writeln(starting(Kinds,Total)),nl,
  do((
    a_similarity(Similarity),
    writeln(testing(Similarity)),
    guess_count(Similarity,Kinds,C),
    Perc is round(10000*C/Total)/100,
    writeln([Similarity,Kinds]:[C/Total=Perc,'%']),nl
  )).

guess_count(Similarity,Kinds,C):-
  aggregate_all(count,(member(Kind,Kinds),at(_,Kind,Y,T,_Ns),cat_guess(Similarity,T,_,L),Y=L),C).

cat_guess(Similarity,Term,Sim,Label):-
  aggregate_all(max(Sim,Label),sim_cat(Similarity,Term,Sim,Label),max(Sim,Label)).


sim_cat(Similarity,Term,Sim,Label):-
  label_to_term(Label,CatTerm),
  call(Similarity,Term,CatTerm,Sim).

label_to_term(Label,Term):-
  cat(Label,Category),
  desc(Category,Term).


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


nlp_guessable_with(Similarity,N):-
   tester_at(N,Y,T,_),
   once((
     trainer_at(_M,Y,OtherT,_),
     call(Similarity,T,OtherT,Sim),
     Sim>0
   )).

nlp_guessables_with(Similarity,Count):-
  aggregate_all(count,N,nlp_guessable_with(Similarity,N),Count).

nlp_guessable_ratio(Similarity,GCount/TCount=R):-
  testables(TCount),
  nlp_guessables_with(Similarity,GCount),
  R is GCount/TCount.


content_limits:-
  do((
    a_similarity(Similarity),
    nlp_guessable_ratio(Similarity,Result),
    writeln((Similarity->Result))
  )).

% computes limits on what can be achieved
% based on info about the network's structure
% or the content attached to its nodes
limits:-
  network_limits,
  content_limits.

