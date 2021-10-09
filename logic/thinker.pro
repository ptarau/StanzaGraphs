%:-set_prolog_flag(stack_limit,34359738368).

param(show_each_nth,100).
param(max_neighbor_nodes,100).
param(max_peer_nodes,256).
param(depth_for_edges,4).
param(path_similarity_start,1).
param(max_termlet_size,10).
param(favor_the_neighbors,true).
param(train_tags,[tr,va]).
param(test_tags,[te]).

param(similarity,shared_path_similarity).

a_similarity(S):-member(S,[
  mock_similarity,
  shared_path_similarity,
  forest_path_similarity,
  termlet_similarity,
  node_jaccard_similarity,
  edge_jaccard_similarity]
  ).

% mock_similarity(A,B,S) % 64 -> 0.0.6732
% shared_path_similarity(A,B,S)
% list_path_similarity(A,B,S). % 64 -> 0.6824
% set_path_similarity(A,B,S). % 64 ->
% termlet_similarity(A,B,S). % 64-> accuracy=0.6412
% node_jaccard_similarity(A,B,S). % 64->0.6814
% edge_jaccard_similarity(A,B,S). % 64->0.6256 depth 3


trainer_at(N,Y,T,Ns):-
  param(train_tags,TrTags),
  member(Tag,TrTags),
  at(N,Tag,Y,T,Ns).

tester_at(N,Y,T,Ns):-
  param(test_tags,TeTags),
  member(Tag,TeTags),
  at(N,Tag,Y,T,Ns).

similarity(A,B,Sim):-param(similarity,F),call(F,A,B,Sim).

accuracy(Acc):-
   param(test_tags,TestTags),
   count_nodes(TestTags,Total), % test nodes
   aggregate_all(count,correct_label,Success),
   Acc is Success/Total.

correct_label:-inferred_label(YtoGuess, YasGuessed),YtoGuess=YasGuessed.

inferred_label(YtoGuess, YasGuessed):-
   writeln('STARTING'),
   param(show_each_nth,M),
   param(max_neighbor_nodes,MaxNodes),
   param(max_peer_nodes,MaxPeerNodes),
   most_freq_class(FreqClass),
   tester_at(N,YtoGuess,MyTextTerm,Neighbors),
   (N mod M=:=0->writeln(starting(N));true),
   ( param(favor_the_neighbors,true),
     at_most_n_sols(MaxNodes,YW,
          neighbor_data(MyTextTerm,Neighbors,YW),YsAndWeights)->true
   ; description_data(MyTextTerm,YsAndWeights)->
          write('-'),true
   ; at_most_n_sols(MaxPeerNodes,YW,
          peer_data(MyTextTerm,YW),YsAndWeights)->
          write('.'),true
   ;
     writeln('*** no peer found, assigned most frequent'(N=FreqClass)),
     YsAndWeights=[FreqClass-1.0]
   ),
   vote_for_best_label(YsAndWeights,YasGuessed),
   (N mod M=:=0->writeln(done(N,(YasGuessed->YtoGuess))),nl;true).

vote_for_best_label(YsAndWeights,YasGuessed):-
   keygroups(YsAndWeights,YsAndWeightss),
   maplist(sum_up,YsAndWeightss,WeightAndYs),
   max_member(_-YasGuessed,WeightAndYs).

neighbor_data(MyTextTerm,Neighbors,Y-Weight):-
  member(M,Neighbors),
  similar_to(MyTextTerm,M,Y,Weight).


description_data(MyTextTerm,[Label-Sim]):-
 param(similarity,Similarity),
 description_data(Similarity,MyTextTerm,[Label-Sim]).

description_data(Similarity,MyTextTerm,[Label-Sim]):-
  cat_guess(Similarity,MyTextTerm,Sim1,Label),
  proto_guess(Similarity,MyTextTerm,[Label-Sim2]),
  Sim is (Sim1+Sim2)/2,
  Sim>0.

proto_guess(Similarity,MyTextTerm,[Label-Sim]):-
  most_cited(Label,_,M),
  trainer_at(M,Label,Term,_),
  call(Similarity,MyTextTerm,Term,Sim),
  Sim>0.

peer_data(MyTextTerm,Y-Weight):-
  similar_to(MyTextTerm,_Any,Y,Weight).

similar_to(MyTextTerm, M, Y,Weight):-
   trainer_at(M,Y,ItsTextTerm,_NNeighbors),
   %/*
   once((
     % ensure Y is shared with at least one neighbor
     member(MM,NNeighbors),
     trainer_at(MM,Y,_,_)
   )),
   %*/
   similarity(MyTextTerm,ItsTextTerm,Weight),
   Weight>0.

keygroups(Ps,KXs):-
   keysort(Ps,Ss),
   group_pairs_by_key(Ss,KXs).

sum_up(Y-Ws,Weight-Y):-sumlist(Ws,Weight).

at_most_n_sols(N,X,G,Xs):-once(findnsols(N,X,G,Xs)),Xs=[_|_].


count_nodes(Kinds,Count):-
   aggregate_all(count,(member(Kind,Kinds),at(_N,Kind,_Y,_Term,_Ns)),Count).

most_freq_class(FreqClass):-
   findall(Y-1,at(_N,_Kind,Y,_Term,_Ns),YNs),
   keygroups(YNs,YOnes),
   maplist(sum_up,YOnes,YCounts),
   aggregate_all(
     max(Count,Y),
     member(Count-Y,YCounts),
     max(Count,FreqClass)
   ).

label_to_term(Label,Term):-
  cat(Label,Category),
  desc(Category,Term).

sim_cat(Similarity,Term,Sim,Label):-
  label_to_term(Label,CatTerm),
  call(Similarity,Term,CatTerm,Sim).

cat_guess(Similarity,Term,Sim,Label):-
  aggregate_all(max(Sim,Label),sim_cat(Similarity,Term,Sim,Label),max(Sim,Label)).

guess_count(Similarity,Kinds,C):-
  aggregate_all(count,(member(Kind,Kinds),at(_,Kind,Y,T,_Ns),cat_guess(Similarity,T,_,L),Y=L),C).

most_cited_with(Label,Froms,Tos,Count,Old):-
   cat(Label,_),
   aggregate(max(Count,Old),
      count_with(Label,Froms,Tos,Count,Old),
      max(Count,Old)).

count_with(Label,Froms,Tos,Count,Old):-
   member(To,Tos),
   at(Old,To,Label,_,_),
   aggregate(count,cited_with(Label,Froms,Old),Count).

cited_with(Label,Froms,Old):-
  member(From,Froms),
  at(_New,From,Label,_,Ns),
  member(Old,Ns).


most_cited:-
   tell('most_cited.pro'),
   do((
     most_cited_with(Label,[tr,va],[tr,va],Count,Cited),
     portray_clause(most_cited(Label,Cited,Count))
   )),
   told,
   true.

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


do(Gs):-Gs,fail;true.

param:-listing(param/2).

go:-
   param,
   time(accuracy(Acc)),
   param,
   writeln(accuracy=Acc).

