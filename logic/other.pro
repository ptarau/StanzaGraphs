% possibly interesting but not used

:-ensure_loaded('cat_terms.pro').
:-ensure_loaded('most_cited.pro').


% guessing the closest with several similarities

guess:-
   %guess([tr,va]),
   guess([te]).

guess(Kinds):-
  count_nodes(Kinds,Total),
  writeln(starting(Kinds,Total)),nl,
  do((
    is_similarity(Similarity,_),
    writeln(testing(Similarity)),
    guess_count(Similarity,Kinds,C),
    Perc is round(10000*C/Total)/100,
    writeln([Similarity,Kinds]:[C/Total=Perc,'%']),nl
  )).



guess_count(Similarity,Kinds,C):-
  aggregate_all(count,(member(Kind,Kinds),at(_,Kind,Y,T,_Ns),cat_guess(Similarity,T,_,L),Y=L),C).

cat_guess(Similarity,Term,Sim,Label):-
  aggregate_all(max(Sim,Label),sim_cat(Similarity,Term,Sim,Label),max(Sim,Label)).

count_nodes(Kinds,Count):-
  aggregate_all(count,(member(Kind,Kinds),at(_N,Kind,_Y,_Term,_Ns)),Count).

sim_cat(Similarity,Term,Sim,Label):-
  label_to_term(Label,CatTerm),
  call(Similarity,Term,CatTerm,Sim).

label_to_term(Label,Term):-
  cat(Label,Category),
  desc(Category,Term).
  
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


description_data(MyTextTerm,[Label-Sim]):-
 param(similarity,Similarity),
 aggregate(max(Sim,Label),
    proto_guess(Similarity,MyTextTerm,Label-Sim),max(Sim,Label)),
    Sim>0.1.

proto_guess(Similarity,MyTextTerm,Label-Sim):-

  most_cited(Label,_,M),
  trainer_at(M,Label,Term,_),
  call(Similarity,MyTextTerm,Term,Sim).

% using most cited in each class as a prototype


most_cited:-
   %tell('most_cited.pro'), % lomng to compute, saved to file
   do((
     most_cited_with(Label,Count,Cited),
     portray_clause(most_cited(Label,Cited,Count))
   )),
   %told,
   true.


most_cited_with(Label,Count,Old):-
   cat(Label,_),
   aggregate(max(Count,Old),
      count_with(Label,Count,Old),
      max(Count,Old)).
      
  