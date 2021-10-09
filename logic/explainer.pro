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
