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

// Put your code here.

(LOOP)
    @i
    M=0
    @SET_COLOR
    0; JMP
    (FOR)
        @CHECK 
        0; JMP
        @DRAW
        0; JMP

(DRAW)
    @color 
    D=M
    @ptr
    A=M
    M=D

    @i
    M=M+1
    @FOR
    0; JMP    

(CHECK)
    @i
    D=M
    @SCREEN
    D=D+A
    @ptr
    M=D

    @KBD
    D=D-A
    @DRAW
    D; JLT
    @LOOP
    0; JMP

(SET_COLOR)    
    @KBD
    D=M
    @BLACK
    D; JGT
    @WHITE
    0; JMP

(WHITE)
    @color
    M=0
    @FOR
    0; JMP

(BLACK)
    @color
    M=-1
    @FOR
    0; JMP



    
