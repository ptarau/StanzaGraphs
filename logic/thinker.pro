%:-set_prolog_flag(stack_limit,34359738368).

param(show_each_nth,100).
param(max_neighbor_nodes,100).
param(max_peer_nodes,4).
param(neighbor_kind,diverse). % any, diverse, none
param(depth_for_edges,4).
param(path_similarity_start,1).
param(max_termlet_size,4).
param(train_tags,[tr,va]).
param(test_tags,[te]).

param(similarity,node_jaccard_similarity).

is_similarity(mock_similarity,0.0).
is_similarity(node_jaccard_similarity,0.01).
is_similarity(shared_path_similarity,1.0).
is_similarity(edge_jaccard_similarity,0.01).
is_similarity(forest_path_similarity,1.0).
is_similarity(termlet_similarity,1.0).

similarity(A,B,Sim):-
   param(similarity,F),
   is_similarity(F,MinVal),
   call(F,A,B,Sim),
   Sim>MinVal.

accuracy(Acc):-
   test_size(Total), % total number of test nodes
   aggregate_all(count,correct_label,Success),
   Acc is Success/Total.

correct_label:-inferred_label(YtoGuess,YasGuessed),YtoGuess=YasGuessed.

inferred_label(YtoGuess, YasGuessed):-
   writeln('STARTING'),
   param(show_each_nth,M),
   param(max_neighbor_nodes,MaxNodes),
   param(neighbor_kind,NK), % NK is one of any, diverse, none
   most_freq_class(FreqClass),
   select_diverse_peers(Peers),
   tester_at(N,YtoGuess,MyTextTerm,Neighbors),
   (N mod M=:=0->writeln(starting(N));true),
   ( NK\=none,at_most_n_sols(MaxNodes,YW,
       neighbor_data(NK,Peers,MyTextTerm,Neighbors,YW),YsAndWeights)->true
   ; peer_data(Peers,MyTextTerm,YsAndWeights)->write('.'),true
   ; write('!'),YsAndWeights=[FreqClass-1.0]
   ),
   vote_for_best_label(YsAndWeights,YasGuessed),
   (N mod M=:=0->writeln(done(N,(YasGuessed->YtoGuess))),nl;true).

vote_for_best_label(YsAndWeights,YasGuessed):-
   keygroups(YsAndWeights,YsAndWeightss),
   maplist(sum_up,YsAndWeightss,WeightAndYs),
   max_member(_-YasGuessed,WeightAndYs).

neighbor_data(any,_,MyTextTerm,Neighbors,Y-Weight):-
  member(M,Neighbors),
  similar_to(MyTextTerm,M,Y,Weight).

neighbor_data(diverse,Peers,MyTextTerm,Neighbors,Y-Weight):-
  param(max_peer_nodes,K),
  length(Peers,L),
  LabelCount is L//K,
  %writeln('!!!!',LabelCount),
  select_diverse_neighbor(K,LabelCount,Neighbors,M),
  similar_to(MyTextTerm,M,Y,Weight).


select_diverse_neighbor(K,LabelCount,Ms, P):-
  between(0,LabelCount,Label),
  at_most_n_sols(K,P,(member(P,Ms),trainer_at(P,Label,_T,_)),Ps),
  member(P,Ps).

peer_data(Peers,MyTextTerm,YWs):-
  findall(YW,one_peer_data(Peers,MyTextTerm,YW),YWs).

one_peer_data(Peers,MyTextTerm,Y-Weight):-
  member(P,Peers),
  similar_to(MyTextTerm,P,Y,Weight).

select_diverse_peers(Peers):-
   param(max_peer_nodes,K),
   count_labels(YCount),
   findall(P,
   (
     between(0,YCount,Label),
     at_most_n_sols(K,P,trainer_at(P,Label,_,_),Ps),
     member(P,Ps)
   ),
   Peers).


similar_to(MyTextTerm, M, Y,Weight):-
   trainer_at(M,Y,ItsTextTerm,_NNeighbors),
   /*
   once((
     % ensure Y is shared with at least one neighbor
     member(MM,NNeighbors),
     trainer_at(MM,Y,_,_)
   )),
   */
   similarity(MyTextTerm,ItsTextTerm,Weight).

keygroups(Ps,KXs):-
   keysort(Ps,Ss),
   group_pairs_by_key(Ss,KXs).

sum_up(Y-Ws,Weight-Y):-sumlist(Ws,Weight).

at_most_n_sols(N,X,G,Xs):-once(findnsols(N,X,G,Xs)),Xs=[_|_].

trainer_at(N,Y,T,Ns):-
  param(train_tags,TrTags),
  member(Tag,TrTags),
  at(N,Tag,Y,T,Ns).

tester_at(N,Y,T,Ns):-
  param(test_tags,TeTags),
  member(Tag,TeTags),
  at(N,Tag,Y,T,Ns).


count_labels(Count):-
  aggregate_all(count,distinct(Y,trainer_at(_,Y,_,_)),Count).

test_size(Count):-
   aggregate_all(count,N,tester_at(N,_,_,_),Count).

most_freq_class(FreqClass):-
   findall(Y-1,trainer_at(_N,Y,_Term,_Ns),YNs),
   keygroups(YNs,YOnes),
   maplist(sum_up,YOnes,YCounts),
   aggregate_all(
     max(Count,Y),
     member(Count-Y,YCounts),
     max(Count,FreqClass)
   ).


do(Gs):-Gs,fail;true.

param:-listing(param/2).

go:-
   param,
   time(accuracy(Acc)),
   param,
   writeln(accuracy=Acc).

