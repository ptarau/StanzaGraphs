%:-set_prolog_flag(stack_limit,34359738368).

param(show_each_nth,100).
param(max_neighbor_nodes,100).
param(max_peer_nodes,4).
param(neighbor_kind,any). % diverse, none
param(depth_for_edges,4).
param(path_similarity_start,1).
param(max_termlet_size,10).
param(train_tags,[tr,va]).
param(test_tags,[te]).

param(similarity,node_jaccard_similarity).

a_similarity(S):-member(S,[
  mock_similarity,
  node_jaccard_similarity,
  shared_path_similarity,
  edge_jaccard_similarity,
  forest_path_similarity,
  termlet_similarity
  ]
  ).

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
   param(max_peer_nodes,K),
   most_freq_class(FreqClass),
   select_diverse_peers(K,Peers),
   aggregate_all(count,correct_label(FreqClass,Peers),Success),
   Acc is Success/Total.

correct_label(FreqClass,Peers):-
   inferred_label(FreqClass,Peers,YtoGuess,YasGuessed),
   YtoGuess=YasGuessed.

inferred_label(FreqClass,Peers,YtoGuess, YasGuessed):-
   writeln('STARTING'),
   param(show_each_nth,M),
   param(max_neighbor_nodes,MaxNodes),
   param(neighbor_kind,NK),
   tester_at(N,YtoGuess,MyTextTerm,Neighbors),
   (N mod M=:=0->writeln(starting(N));true),
   ( NK\=none,at_most_n_sols(MaxNodes,YW,
       neighbor_data(NK,MyTextTerm,Neighbors,YW),YsAndWeights)->true
   ; peer_data(Peers,MyTextTerm,YsAndWeights)->write('.'),true
   ; write('!'),YsAndWeights=[FreqClass-1.0]
   ),
   vote_for_best_label(YsAndWeights,YasGuessed),
   (N mod M=:=0->writeln(done(N,(YasGuessed->YtoGuess))),nl;true).

vote_for_best_label(YsAndWeights,YasGuessed):-
   keygroups(YsAndWeights,YsAndWeightss),
   maplist(sum_up,YsAndWeightss,WeightAndYs),
   max_member(_-YasGuessed,WeightAndYs).

neighbor_data(any,MyTextTerm,Neighbors,Y-Weight):-
  member(M,Neighbors),
  similar_to(MyTextTerm,M,Y,Weight).

neighbor_data(diverse,MyTextTerm,Neighbors,Y-Weight):-
  select_diverse_neighbor(4,Neighbors,M),
  similar_to(MyTextTerm,M,Y,Weight).


select_diverse_neighbor(K, Ms, P):-
  cat(Label,_),
  at_most_n_sols(K,P,(member(P,Ms),trainer_at(P,Label,_T,_)),Ps),
  member(P,Ps).

peer_data(Peers,MyTextTerm,YWs):-
  findall(YW,one_peer_data(Peers,MyTextTerm,YW),YWs).

one_peer_data(Peers,MyTextTerm,Y-Weight):-
  member(P,Peers),
  similar_to(MyTextTerm,P,Y,Weight).

select_diverse_peers(K, Peers):-
   findall(P,
   (
     cat(Label,_),
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

