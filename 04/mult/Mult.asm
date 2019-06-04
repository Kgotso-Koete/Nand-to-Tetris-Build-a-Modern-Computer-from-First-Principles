// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)


// pseudo code

// Computes RAM[2] = RAM[0] * RAM[1] otherwise written as...
//          RAM[2] = RAM[0] added to itself, RAM[1] times

//          n = R1 // RAM[1] total number of loops
//          i = 1  // loop counter
//          x = R0 // RAM[0], number being added to itself
//          sum = 0 // the accuumulator

//          LOOP:
//             if i > n go to STOP
//             sum = sum + x
//             i = i + 1
//             go to LOOP
//          STOP:
//             R[2] = sum 

// Put your code here.
@R0
D = M
@R1 
D = M
@n
M = D // n = R0
@i 
M = 1 // start i  at 1
@sum
M = 0 // start sum at 0

(LOOP)
    @i
    D = M  
    @n
    D = D - M
    @STOP
    D;JGT // if i > n, go to stop   

    @sum
    D = M
    @R0
    D = D + M // sum = sum + R0
    @sum
    M = D
    @i
    M = M + 1 // i = i + 1
    @LOOP
    0;JMP

(STOP)
    @sum
    D = M
    @R2
    M = D //RAM[2] = sum

(END)
    @END  
    0;JMP

