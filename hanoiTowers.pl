%program to solve the towers of hanoi problem in prolog
%to use, type "move(3,source,target,interim). into the console
%this solves the towers of hanoi problem with 3 towers
%changing this number increases the amount of towers, which drastically
%increases the amount of moves needed and the computational power required


move(1, X, Y, _)	:-
    write('Move top disk from: '),
    write(X),
    write(' to '),
    write(Y),
    nl.

move(N, X, Y, Z)	:-
    N > 1,
    M is N - 1,
    move(M, X, Z, Y),
    move(1, X, Y, _),
    move(M, Z, Y, X).