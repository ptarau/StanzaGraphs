c:-make.

:-ensure_loaded('OUTPUT_DIRECTORY/arxiv_all.pro').

accuracy(Acc):-accuracy(64,Acc).

accuracy(MaxNodes,Acc):-
   findall(YtoGuess-YasGuessed,
      inferred_label(MaxNodes,YtoGuess,YasGuessed),Pairs),
   length(Pairs,Total),
   findall(1,member(A-A,Pairs),SameYs),
   length(SameYs,Success),
   Acc is Success/Total.

inferred_label(MaxNodes,YtoGuess, YasGuessed):-
  writeln('STRATING'),
   most_freq_class(FreqClass),
   at(N,te,YtoGuess,MyTextTerm,Neighbors),
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
   (N mod 1 =:=0->writeln(at(N,YtoGuess, YasGuessed));true).

neighbor_data(MyTextTerm,Neighbors,Y-Weight):-
  member(M,Neighbors),
  similar_to(MyTextTerm,M,Y,Weight),
  Weight>2.

peer_data(MyTextTerm,Y-Weight):-
  similar_to(MyTextTerm,_Any,Y,Weight),
  Weight>3.

similar_to(MyTextTerm, M, Y,Weight):-
   at(M,Split,Y,ItsTextTerm,_),
   memberchk(Split,[tr,va]),
   similarity(MyTextTerm,ItsTextTerm,Weight).

keygroups(Ps,KXs):-
   keysort(Ps,Ss),
   group_pairs_by_key(Ss,KXs).


min_sim(2).

fast_path_similarity(A,B,Sim):-
  %term_size(A,S1),term_size(B,S2),writeln(sizes(S1,S2)),
  aggregate_all(max(X),co_path_length(A,B,X),Sim0),
  %writeln(sim=Sim0),
  Sim is 1+Sim0.


co_path_length(S,T,Len):-
   co_path(S,T,Ps),
   %writeln('>>>'+Ps),
   length(Ps,Len).

co_path(S,T,Ps):-co_path(3,S,T,Ps).

co_path(Skip,S,T,Ps):-distinct(Ps,co_path(Skip,S,T,Ps,[])).

co_path(_,S,_)-->{atomic(S)},!.
co_path(_,_,T)-->{atomic(T)},!.
co_path(Skip,S,T)-->
  {functor(S,F,_),functor(T,G,_)},
  maybe_skip(F,G,Skip,SkipLater),
  {arg(_,S,X),arg(_,T,Y)},
  co_path(SkipLater,X,Y).

maybe_skip(F,F,Skip,Skip)-->!,[F].
maybe_skip(_F,_G,Skip,NewSkip)-->{Skip>0,NewSkip is Skip-1}.



sum_up(Y-Ws,W-Y):-sumlist(Ws,W).

at_most_n_sols(N,X,G,Xs):-once(findnsols(N,X,G,Xs)),Xs=[_|_].


% similarity(A,B,S):-mock_similarity(A,B,S).
similarity(A,B,S):-fast_path_similarity(A,B,S).
% similarity(A,B,S):-subtree_similarity(A,B,S).


most_freq_class(FreqClass):-
   findall(Y-1,at(_N,_Kind,Y,_Term,_Ns),YNs),
   keygroups(YNs,YOnes),
   maplist(sum_up,YOnes,YCounts),
   aggregate_all(
     max(Count,Y),
     member(Count-Y,YCounts),
     max(Count,FreqClass)
   ).


go:-accuracy(Acc),writeln(accuracy=Acc).


stest:-
   A=f(a,g(b,p(h(c))),i(d)),
   B=f(e,g(q(h(e)),b),d),
   similarity(A,B,Sim),
   writeln(Sim),
   fail.

stest1:-
   A=f(a,g(b,p(h(c))),i(d)),
   B=f(e,g(q(h(e)),b),d),
   co_path(A,B,Ps),
   writeln(Ps),
   fail.

/*
138139 nodes
38746.005 seconds cpu time for 710,463,593,629 inferences
accuracy=0.6744233895027056
*/
