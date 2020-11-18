// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1

// pop local 0
@SP
M=M-1
A=M
D=M
@0
D=A
@LCL
D=D+M
@saveD
M=D
@SP
A=M
D=M
@saveD
A=M
M=D

// label LOOP_START
(LOOP_START)

// push argument 0
@0
D=A
@ARG
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// push local 0
@0
D=A
@LCL
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// add
@SP
AM=M-1
D=M
A=A-1
M=D+M

// pop local 0	
@SP
M=M-1
A=M
D=M
@0	
D=A
@LCL
D=D+M
@saveD
M=D
@SP
A=M
D=M
@saveD
A=M
M=D

// push argument 0
@0
D=A
@ARG
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1

// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D

// pop argument 0
@SP
M=M-1
A=M
D=M
@0
D=A
@ARG
D=D+M
@saveD
M=D
@SP
A=M
D=M
@saveD
A=M
M=D

// push argument 0
@0
D=A
@ARG
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// if-goto LOOP_START
@SP
AM=M-1
D=M
@LOOP_START
D;JNE

// push local 0
@0
D=A
@LCL
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

