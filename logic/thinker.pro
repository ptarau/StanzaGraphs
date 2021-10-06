%:-set_prolog_flag(stack_limit,34359738368).

c:-make.

:-ensure_loaded('OUTPUT_DIRECTORY/arxiv_all.pro').
:-ensure_loaded('sims.pro').
:-ensure_loaded('explainer.pro').

param(show_each_nth,100).
param(max_nodes,64).
param(depth_for_edges,4).
param(path_similarity_start,1).
param(path_similarity_skip,1).
param(favor_the_neighbors,true).

param(similarity,set_path_similarity).

% mock_similarity(A,B,S) % 64 -> 0.0.6732
% list_path_similarity(A,B,S). % 64 -> 0.6824
% set_path_similarity(A,B,S). % 64 ->
% slow_path_similarity(A,B,S)
% subtree_similarity(A,B,S). % 64-> accuracy=0.6412
% node_jaccard_similarity(A,B,S). % 64->0.6814
% edge_jaccard_similarity(A,B,S). % 64->0.6256 depth 3

similarity(A,B,Sim):-param(similarity,F),call(F,A,B,Sim).

accuracy(Acc):-
   count_nodes('te',Total), % test nodes
   aggregate_all(count,correct_label,Success),
   Acc is Success/Total.

correct_label:-inferred_label(YtoGuess, YasGuessed),YtoGuess=YasGuessed.

inferred_label(YtoGuess, YasGuessed):-
   writeln('STARTING'),
   param(show_each_nth,M),
   param(max_nodes,MaxNodes),
   most_freq_class(FreqClass),
   at(N,te,YtoGuess,MyTextTerm,Neighbors),
   (N mod M=:=0->writeln(starting(N));true),
   ( param(favor_the_neighbors,true),
     at_most_n_sols(MaxNodes,YW,
          neighbor_data(MyTextTerm,Neighbors,YW),YWs)->true
   ; at_most_n_sols(MaxNodes,YW,
          peer_data(MyTextTerm,YW),YWs)->true
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
   at(M,Split,Y,ItsTextTerm,_),
   memberchk(Split,[tr,va]),
   similarity(MyTextTerm,ItsTextTerm,Weight),
   Weight>0.

keygroups(Ps,KXs):-
   keysort(Ps,Ss),
   group_pairs_by_key(Ss,KXs).


sum_up(Y-Ws,W-Y):-sumlist(Ws,W).

at_most_n_sols(N,X,G,Xs):-once(findnsols(N,X,G,Xs)),Xs=[_|_].


count_nodes(Kind,Count):-
   aggregate_all(count,at(_N,Kind,_Y,_Term,_Ns),Count).

most_freq_class(FreqClass):-
   findall(Y-1,at(_N,_Kind,Y,_Term,_Ns),YNs),
   keygroups(YNs,YOnes),
   maplist(sum_up,YOnes,YCounts),
   aggregate_all(
     max(Count,Y),
     member(Count-Y,YCounts),
     max(Count,FreqClass)
   ).



go:-
   listing(param),
   time(accuracy(Acc)),
   listing(param),
   writeln(accuracy=Acc).

/*

% 11,047,363 inferences, 3.191 CPU in 3.239 seconds (99% CPU, 3462343 Lips)
param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 2).
param(favor_the_neighbors, true).
param(similarity, mock_similarity).

accuracy=0.6732506223895645
true.

% 12,545,534,366 inferences, 776.115 CPU in 778.681 seconds (100% CPU, 16164536 Lips)
param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 0).
param(favor_the_neighbors, true).
param(similarity, fast_path_similarity).

accuracy=0.6751846593831656
true.



% 9,128,274,384 inferences, 580.873 CPU in 581.297 seconds (100% CPU, 15714761 Lips)
param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 2).
param(favor_the_neighbors, true).
param(similarity, fast_path_similarity).

accuracy=0.6600004114972327
true.


param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 2).
param(favor_the_neighbors, false).
param(similarity, node_jaccard_similarity).

accuracy=0.05865893051869226


param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 2).
param(favor_the_neighbors, false).
param(similarity, mock_similarity).

accuracy=0.05861778079542415

param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 2).
param(favor_the_neighbors, false).
param(similarity, edge_jaccard_similarity).

accuracy=0.07365800464991873
true.



% 92,001,465,966 inferences, 4940.995 CPU in 4944.615 seconds (100% CPU, 18620027 Lips)
param(show_each_nth, 100).
param(max_nodes, 64).
param(depth_for_edges, 4).
param(path_similarity_start, 2).
param(favor_the_neighbors, false).
param(similarity, fast_path_similarity).

accuracy=0.05861778079542415

*/
