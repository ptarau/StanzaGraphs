%:-set_prolog_flag(stack_limit,34359738368).

c:-make.

:-ensure_loaded('cat_terms.pro').
:-ensure_loaded('cs_cats.pro').
:-ensure_loaded('OUTPUT_DIRECTORY/arxiv_all.pro').
:-ensure_loaded('sims.pro').
:-ensure_loaded('explainer.pro').


param(show_each_nth,100).
param(max_neighbor_nodes,100).
param(max_peer_nodes,256).
param(depth_for_edges,4).
param(path_similarity_start,1).
param(max_termlet_size,10).
param(favor_the_neighbors,true).
param(train_tags,[tr,va]).
param(test_tags,[te]).


param(similarity,mock_similarity).

a_similarity(S):-member(S,[
  mock_similarity,arg_path_similarity,list_path_similarity,set_path_similarity,
  termlet_similarity,node_jaccard_similarity,edge_jaccard_similarity]
  ).

% mock_similarity(A,B,S) % 64 -> 0.0.6732
% arg_path_similarity(A,B,S)
% list_path_similarity(A,B,S). % 64 -> 0.6824
% set_path_similarity(A,B,S). % 64 ->
% termlet_similarity(A,B,S). % 64-> accuracy=0.6412
% node_jaccard_similarity(A,B,S). % 64->0.6814
% edge_jaccard_similarity(A,B,S). % 64->0.6256 depth 3

similarity(A,B,Sim):-param(similarity,F),call(F,A,B,Sim).

accuracy(Acc):-
   param(test_tags,TestTags),
   count_nodes(TestTags,Total), % test nodes
   aggregate_all(count,correct_label,Success),
   Acc is Success/Total.

correct_label:-inferred_label(YtoGuess, YasGuessed),YtoGuess=YasGuessed.

inferred_label(YtoGuess, YasGuessed):-
   param(test_tags,TestTags),
   writeln('STARTING'),
   param(show_each_nth,M),
   param(max_neighbor_nodes,MaxNodes),
   param(max_peer_nodes,MaxPeerNodes),
   most_freq_class(FreqClass),
   member(TestTag,TestTags),
   at(N,TestTag,YtoGuess,MyTextTerm,Neighbors),
   (N mod M=:=0->writeln(starting(N));true),
   ( param(favor_the_neighbors,true),
     at_most_n_sols(MaxNodes,YW,
          neighbor_data(MyTextTerm,Neighbors,YW),YWs)->true

   ; description_data(MyTextTerm,YWs)->true
   ; at_most_n_sols(MaxPeerNodes,YW,
          peer_data(MyTextTerm,YW),YWs)->
          write('.'),true
   ;
     writeln('*** no peer found, assigned'(N=FreqClass)),
     YWs=[FreqClass-1.0]
   ),
   keygroups(YWs,YWss),
   maplist(sum_up,YWss,WYs),
   (max_member(_-YasGuessed,WYs)->true;writeln(unexpected_fail=N)),
   (N mod M=:=0->writeln(done(N,(YasGuessed->YtoGuess))),nl;true).

neighbor_data(MyTextTerm,Neighbors,Y-Weight):-
  member(M,Neighbors),
  similar_to(MyTextTerm,M,Y,Weight).

peer_data(MyTextTerm,Y-Weight):-
  similar_to(MyTextTerm,_Any,Y,Weight).

similar_to(MyTextTerm, M, Y,Weight):-
   param(train_tags,TrainTags),
   member(TrainTag,TrainTags),
   at(M,TrainTag,Y,ItsTextTerm,_),
   similarity(MyTextTerm,ItsTextTerm,Weight),
   Weight>0.

keygroups(Ps,KXs):-
   keysort(Ps,Ss),
   group_pairs_by_key(Ss,KXs).


sum_up(Y-Ws,W-Y):-sumlist(Ws,W).

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

cat_guess(Similarity,Term,Label,Sim):-
  aggregate_all(max(Sim,Label),sim_cat(Similarity,Term,Sim,Label),max(Sim,Label)).


description_data(MyTextTerm,[Y-W]):-
  cat_guess(similarity,MyTextTerm,Y,W),
  W>0.

guess_count(Similarity,Kinds,C):-
  aggregate_all(count,(member(Kind,Kinds),at(_,Kind,Y,T,_Ns),cat_guess(Similarity,T,_,L),Y=L),C).


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

