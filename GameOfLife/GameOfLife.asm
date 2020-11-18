// The game of life world consists of 2D grid 16x32, the grid is mapped in memory:
// RAM[100] == grid(0, 0)
// RAM[132] == grid(1, 0)
// RAM[611] == grid(16, 31)
//
// RAM[99] contains number of generations to iterate over the Game of life world (aka grid)
//
// Iteration rules:
// For a space that is 'populated':
// * Each cell with one or no neighbors dies, as if by solitude.
// * Each cell with four or more neighbors dies, as if by overpopulation.
// * Each cell with two or three neighbors survives.
//
// For a space that is 'empty' or 'unpopulated'
// * Each cell with three neighbors becomes populated.
//
// initial values are set by test. The are only two values allowed:
// 1 -- the cell is populated
// 0 -- the cell is empty

// your code here


(RAM99)
    @99
    D=M
    @ITR
    M=D

(ITRERATIONS)
    @DRAW
    0;JMP
    (LIFE_CYCLE)
        @99
        D=A
        @CURR
        M=D
        @ITR
        D=M
        M=M-1
        @LOOP
        D;JGT
        @END
        0;JMP

(LOOP)
    @CURR
    M=M+1
    D=M
    @611
    D=D-A
    @CHECK
    D;JLE
    @99
    D=A
    @CURR
    M=D
    @RESPAWN
    0;JMP

(CHECK)
    @CURR
    A=M
    D=M
    @UP
    D;JGT
    @LOOP
    0;JMP

(UP)
    @32
    D=A
    @CURR
    D=M+D
    @611
    D=D-A
    @RBORDER
    D;JGT
    @32
    D=A
    @CURR
    D=M+D
    @1000
    A=A+D
    M=M+1
    @RBORDER
    0;JMP

(RIGHT)
    @CURR
    D=M+1
    @611
    D=D-A
    @UPRIGHT
    D;JGT
    @CURR
    D=M+1
    @1000
    A=A+D
    M=M+1
    @UPRIGHT
    0;JMP

(UPRIGHT)
    @32
    D=A
    @CURR
    D=M+D
    D=D+1
    @611
    D=D-A
    @DOWNRIGHT
    D;JGT
    @32
    D=A
    @CURR
    D=M+D
    D=D+1
    @1000
    A=A+D
    M=M+1
    @DOWNRIGHT
    0;JMP

(DOWNRIGHT)
    @32
    D=A
    @CURR
    D=M-D
    D=D+1
    @611
    D=D-A
    @LBORDER
    D;JGT
    @32
    D=A
    @CURR
    D=M-D
    D=D+1
    @1000
    A=A+D
    M=M+1
    @LBORDER
    0;JMP

(LEFT)
    @CURR
    D=M-1
    @611
    D=D-A
    @UPLEFT
    D;JGT
    @CURR
    D=M-1
    @1000
    A=A+D
    M=M+1
    @UPLEFT
    0;JMP

(UPLEFT)
    @32
    D=A
    @CURR
    D=M+D
    D=D-1
    @611
    D=D-A
    @DOWNLEFT
    D;JGT
    @32
    D=A
    @CURR
    D=M+D
    D=D-1
    @1000
    A=A+D
    M=M+1
    @DOWNLEFT
    0;JMP

(DOWNLEFT)
    @32
    D=A
    @CURR
    D=M-D
    D=D-1
    @611
    D=D-A
    @DOWN
    D;JGT
    @32
    D=A
    @CURR
    D=M-D
    D=D-1
    @1000
    A=A+D
    M=M+1
    @DOWN
    0;JMP

(DOWN)
    @32
    D=A
    @CURR
    D=M-D
    @611
    D=D-A
    @LOOP
    D;JGT
    @32
    D=A
    @CURR
    D=M-D
    @1000
    A=A+D
    M=M+1
    @LOOP
    0;JMP

(RBORDER)
    @31
    D=A
    @CURR
    D=D&M
    @3
    D=D-A
    @LBORDER
    D;JEQ
    @RIGHT
    0;JMP

(LBORDER)
    @31
    D=A
    @CURR
    D=D&M
    @4
    D=D-A
    @DOWN
    D;JEQ
    @LEFT
    0;JMP

(RESPAWN)
    @CURR
    M=M+1
    D=M
    @611
    D=D-A
    @SURVIVES
    D;JLE
    @ITRERATIONS
    0;JMP

(SURVIVES)
    @CURR
    D=M
    @1000
    A=A+D
    D=M
    M=0
    @3
    D=D-A
    @LIVE
    D;JEQ
    D=D+1
    @KEEPLIVE
    D;JEQ
    @DIE
    0;JMP

(LIVE)
    @CURR
    A=M
    M=1
    @RESPAWN
    0;JMP

(KEEPLIVE)
    @CURR
    A=M
    D=M
    @LIVE
    D;JGT
    @DIE
    0;JMP

(DIE)
    @CURR
    A=M
    M=0
    @RESPAWN
    0;JMP    

(DRAW)
    @PXL
    M=0
    @99
    D=A
    @COLOR
    M=D
    (SCRN_LOOP)
        @PXL
        D=M
        @7200
        D=D-A
        @LIFE_CYCLE
        D;JGT
        @COLOR
        M=M+1
        @SCREEN
        D=A
        @PXL
        D=D+M
        @PTR
        M=D
        @31
        D=A
        @PXL
        M=M+1
        D=D&M
        @NEXTPXL
        D;JEQ
        (CONTINUE)
        @idx
        M=0
        (FOR16)
            @COLOR
            A=M
            D=-M
            @PTR
            A=M
            M=D
            @32
            D=A
            @PTR
            M=M+D
            @15
            D=A
            @idx
            M=M+1
            D=D&M
            @SCRN_LOOP
            D;JEQ
            @FOR16  
            0;JMP
    (NEXTPXL)
        @448
        D=A
        @PXL
        M=M+D
        @CONTINUE
        0;JMP
       
(END)
    @END
    0;JMP
