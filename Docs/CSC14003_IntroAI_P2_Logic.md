# 1 Overview

Hashiwokakero, also known as Bridges or Hashi, is a logic puzzle that challenges players to connect
numbered islands with a specific number of bridges while following a set of simple rules. Published
by Nikoli, this puzzle requires strategic thinking and careful planning to ensure all islands are
interconnected without exceeding the allowed number of bridges per island. The game has gained
popularity worldwide under different names, such as Ai-Ki-Ai in France, Denmark, the Netherlands, and Belgium. With its elegant design and logical depth, Hashiwokakero offers an engaging
challenge for puzzle enthusiasts of all skill levels.

# 2 Project Description
Hashiwokakero is played on a rectangular grid with no standard size, although the grid itself is not
usually drawn. Some cells start out with (usually encircled) numbers from 1 to 8 inclusive; these
are the ”islands”. The rest of the cells are empty.
In this project, you will develop a Hashiwokakero solver using Conjunctive Normal Form
(CNF) logic. to connect all of the islands by drawing a series of bridges between the islands. The
bridges must follow certain criteria:
+ They must begin and end at distinct islands, travelling a straight line in between.
+ They must not cross any other bridges or islands.
+ They may only run perpendicularly
+ At most two bridges connect a pair of islands
+ The number of bridges connected to each island must match the number on that island.
+ The bridges must connect the islands into a single connected group

In order to solve this problem, you can consider some steps:
1. Define Logical Variables: A logical variable is assigned to each cell of the matrix.
2. (Report) Formulate CNF Constraints: Write constraints for cells containing numbers to
obtain a set of constraint clauses in CNF (note that you need to remove duplicate clauses)
3. (Implement) Automate CNF Generation: Generate CNFs automatically.
4. (Implement) Solve Using PySAT: Using the pysat library to find the value for each variable
and infer the result.
5. (Implement) Apply A Star Search Algorithm: Apply A* to solve the CNF.
6. (Implement) Compare with Other Methods: Program brute-force and backtracking algorithm
to compare their speed (by measuring running time which is how long it takes for a computer
to perform a specific task) and their performance with A*.

# Requirements

## Inputs
Students are required to design at least 10 different input files, named according to the structure input-01.txt, input-02.txt, ..., input-10.txt.

For example
0 , 2 , 0 , 5 , 0 , 0 , 2
0 , 0 , 0 , 0 , 0 , 0 , 0
4 , 0 , 2 , 0 , 2 , 0 , 4
0 , 0 , 0 , 0 , 0 , 0 , 0
0 , 1 , 0 , 5 , 0 , 2 , 0
0 , 0 , 0 , 0 , 0 , 0 , 0
4 , 0 , 0 , 0 , 0 , 0 , 3

where zeros represent empty spaces and other numbers present islands.

## Outputs
The output for above example:
[ ”0” , ”2” , ”=” , ”5” , ”−” , ”−” , ”2” ]
[ ”0” , ”0” , ”0” , ”$” , ”0” , ”0” , ” | ” ]
[ ”4” , ”=” , ”2” , ”$” , ”2” , ”=” , ”4” ]
[ ”$” , ”0” , ”0” , ”$” , ”0” , ”0” , ” | ” ]
[ ”$” , ”1” , ”−” , ”5” , ”=” , ”2” , ” | ” ]
[ ”$” , ”0” , ”0” , ”0” , ”0” , ”0” , ” | ” ]
[ ”4” , ”=” , ”=” , ”=” , ”=” , ”=” , ”3” ]

where “|” means one vertical bridge, “$” means two vertical bridges, “-” means one horizontal
bridge, and “=” means two horizontal bridges.

## Programming language
The source code must be written in Python (3.7 or later). You are allowed to use any supporting
libraries; however, the main algorithms directly related to the search process must be implemented
by you.