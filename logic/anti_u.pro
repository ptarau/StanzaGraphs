anti_unify(A,B,R):-
   au(A,B,R,Xs,[]),
   keygroup(Xs,KVss),
   merge_vars(KVss).
   
   
merge_vars([]).
merge_vars([_-Vs|KVss]):-
    maplist(=(_),Vs),
    merge_vars(KVss).
  
        
au(A,B,R)-->{A==B},!,{R=A}.
au(A,B,R)-->{nonvar(A),nonvar(B)},
  {functor(A,F,N),functor(B,F,N)},
  !,
  {A=..[_|Xs],B=..[_|Ys]},
  aus(Xs,Ys,Zs),
  {R=..[F|Zs]}.
au(A,B,NewVar)-->[g(A,B)-NewVar].

aus([],[],[])-->[].
aus([X|Xs],[Y|Ys],[R|Rs])-->
  au(X,Y,R),
  aus(Xs,Ys,Rs).
 
keygroup(Ps,Gs):-
 keysort(Ps,Qs),
 group_pairs_by_key(Qs,Gs).


tsize(A,R):-var(A),!,R=0.
tsize(A,R):-atomic(A),!,R=1.
tsize(T,R):-T=..[_|Xs],
  maplist(tsize,Xs,Rs),
  sumlist([1|Rs],R).


usim(A,B,Sim):-anti_unify(A,B,R),
  tsize(A,SA),tsize(B,SB),tsize(R,SR),
  Sim is 2*SR/(SA+SB).

udist(A,B,Dist):-usim(A,B,Sim),Dist is 1-Sim.

ppp(X):-portray_clause(X).

g1:-
  A=f(a,a),
  B=f(b,b),
  au(A,B,R,Xs,[]),
  ppp((A+B:-R,Xs)).
  
g2:-
  A=f(a,h(_),a),
  B=f(b,h(_),b),
  anti_unify(A,B,R),
  ppp((R:-A,B)).
  
g3:-
  A=f(a,g(V),h(U),a),
  B=f(b,g(U),h(V),b),
  anti_unify(A,B,R),
  ppp((R:-A,B)).

g4:-
  A=f(a,h(c),a),
  B=f(b,g(c),b),
  anti_unify(A,B,R),
  ppp((R:-A,B)).
  
c:-make.

go:-g4.
