// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


// pseudo code

// While keyboard is pressed:
//      blacken the screen using the loop
// Whiten the screen using the loop 
// Jump back to top of the programme 

// screen filling psuedo code
// addr = SCREEN
// row = 0
// column = 0
// 

// ROWLOOP:
//      if row > 16 goto END
//          RAM[addr] = -1 // 1111111111111111
//          addr = addr + 32 //advances to next row
//          row = row + 1
//          goto ROWLOOP
// END:
//      goto END
//      

(KEYBOARDCHECK)
    @SCREEN
    D = A
    @addr
    M = D // make address the screen's base address = 16,384  
    @8191
    D = A
    @blocklimit
    M = D  
    @block
    M = 0 // row count is 0

    @24576  
    D = M // keyboard address in data stream
    @BLACKEN
    D;JNE // if keyboard is pressed (keyboard register not equal to zero)
    @WHITEN  
    0;JMP // jump back to loop
  
(BLACKEN)
    @block
    D = M
    @blocklimit
    D = D - M
    @KEEPSCREEN
    D;JGT // if i < rowlimit goto end

    @addr
    A = M
    M = -1 // make black (1111111111111111)

    @block
    M = M + 1 // i = i + 1    
    @1
    D = A 
    @addr  
    M = D + M  // move to the next row       
    @BLACKEN
    0;JMP // jump back to loop 

(KEEPSCREEN)
    @24576  
    D = M // keyboard address in data stream
    @BLACKEN
    D;JNE // if keyboard is pressed (keyboard register not equal to zero)
    @24576  
    D = M // keyboard address in data stream 
    @WHITEN
    D;JEQ // if keyboard is pressed (keyboard register not equal to zero)
    @KEEPSCREEN    
    0;JMP // jump back to loop

(WHITEN)
    @block
    D = M
    @blocklimit
    D = D - M
    @KEYBOARDCHECK
    D;JGT // if i < rowlimit goto end

    @addr
    A = M
    M = 0 // make zero (white) 

    @block
    M = M + 1 // i = i + 1    
    @1
    D = A  
    @addr  
    M = D + M  // move to the next row       
    @WHITEN
    0;JMP // jump back to loop    