c:-make.

:-ensure_loaded('OUTPUT_DIRECTORY/arxiv_all.pro').

show:-listing(arxiv).

accuracy(Acc):-accuracy(64,Acc).

accuracy(MaxNodes,Acc):-
   findall(YtoGuess-YasGuessed,all_neighbors_data(MaxNodes,_N,YtoGuess,YasGuessed),Pairs),
   length(Pairs,Total),
   findall(1,member(A-A,Pairs),SameYs),
   length(SameYs,Success),
   Acc is Success/Total.

all_neighbors_data(MaxNodes,N,YtoGuess,YasGuessed):-
  at(N,te,YtoGuess,_,_),
   (N mod 100=:=0->writeln(N);true),
   grouped_neighbor_data(MaxNodes,N,YtoGuess,WYs),

   ( WYs=[]->YasGuessed=0,
             writeln('unexpected'=N)
   ;
     sort(1, @>=, WYs, [_-YasGuessed|_])
   ).

grouped_neighbor_data(MaxNodes,N,YtoGuess,WYs):-
  at(N,te,YtoGuess,_,_),
   at_most_n_sols(MaxNodes,YW,one_neighbor_data(N,YtoGuess,YW),YWs),
   keygroups(YWs,YWss),
   maplist(sum_up,YWss,WYs).

sum_up(Y-Ws,W-Y):-sumlist(Ws,W).

at_most_n_sols(N,X,G,Xs):-once(findnsols(N,X,G,Xs)).

one_neighbor_data(N,YtoGuess,Y-Weight):-
 at(N,te,YtoGuess,MyTextTerm,Neighbors),
  ( Neighbors=[_|_]->
    member(M,Neighbors),
    similar_to(MyTextTerm,M,Y,Weight)
  ; similar_to(MyTextTerm,_Any,Y,Weight),
    Weight>3
    %,writeln(far=N:Weight)
  ).

similar_to(MyTextTerm, M, Y,Weight):-
   at(M,Split,Y,ItsTextTerm,_),
    memberchk(Split,[tr,va]),
    similarity(MyTextTerm,ItsTextTerm,Weight).


keygroups(Ps,KXs):-
   keysort(Ps,Ss),
   group_pairs_by_key(Ss,KXs).

similarity(A,B,Sim):-
   aggregate_all(sum(Sim),sharing_count(A,B,Sim),Sim).
   %writeln(sim=Sim).

sharing_count(A,B,Res):-
  sub_term(T,A),
  occurrences_of_term(T,B,Count),
  Count>0,
  term_size(T,Size),
  Res is (1+Size)*Count.

go1:-one_neighbor_data(N,Y,R),writeln([N,Y,R]),fail.
go2:-grouped_neighbor_data(16,N,Y,R),writeln([N,Y,R]),fail.

go3:-all_neighbors_data(16,N,Y,R),writeln([N,Y,R]),fail.

go:-accuracy(Acc),writeln(accuracy=Acc).


stest:-
   A=f(a,g(b,h(c)),i(d)),
   B=f(e,g(h(e),b),d),
   similarity(A,B,Sim),
   writeln(Sim),
   fail.

/*
138139 nodes
38746.005 seconds cpu time for 710,463,593,629 inferences
accuracy=0.6744233895027056
*/
