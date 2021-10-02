:-set_prolog_flag(stack_limit,17179869184).

c:-make.

:-ensure_loaded('OUTPUT_DIRECTORY/arxiv_all.pro').
:-ensure_loaded('sims.pro').

accuracy(Acc):-time(accuracy(64,Acc)).

accuracy(MaxNodes,Acc):-
   count_nodes('te',Total), % test nodes
   aggregate_all(count,correct_label(MaxNodes),Success),
   Acc is Success/Total.

correct_label(MaxNodes):-inferred_label(MaxNodes,Y,Y).

inferred_label(MaxNodes,YtoGuess, YasGuessed):-
   writeln('STARTING'),M=1000,
   most_freq_class(FreqClass),
   at(N,te,YtoGuess,MyTextTerm,Neighbors),
   (N mod M=:=0->writeln(starting(N));true),
   ( at_most_n_sols(MaxNodes,YW,
     neighbor_data(MyTextTerm,Neighbors,YW),YWs)->true
   ; at_most_n_sols(MaxNodes,YW,peer_data(MyTextTerm,YW),YWs)->true
   ; YWs=[FreqClass-1.0]
     ,writeln('*** no peer found, assigned'(N=FreqClass))
   ),
   keygroups(YWs,YWss),
   maplist(sum_up,YWss,WYs),
   aggregate_all(max(Count,Y),
       member(Count-Y,WYs),
       max(Count,YasGuessed)),
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


similarity(A,B,S):-mock_similarity(A,B,S). % 120-> 0.66734
% similarity(A,B,S):-fast_path_similarity(A,B,S).
% similarity(A,B,S):-slow_path_similarity(A,B,S).
% similarity(A,B,S):-subtree_similarity(A,B,S).
% similarity(A,B,S):-node_jaccard_similarity(A,B,S).
% similarity(A,B,S):-edge_jaccard_similarity(A,B,S).


go:-accuracy(Acc),writeln(accuracy=Acc).

