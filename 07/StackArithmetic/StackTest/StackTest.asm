@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND1
D;JEQ
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP1
D;JEQ
(TRUE_COND1)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP1)
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND2
D;JEQ
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP2
D;JEQ
(TRUE_COND2)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP2)
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND3
D;JEQ
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP3
D;JEQ
(TRUE_COND3)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP3)
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND4
D;JGT
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP4
D;JEQ
(TRUE_COND4)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP4)
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND5
D;JGT
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP5
D;JEQ
(TRUE_COND5)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP5)
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND6
D;JGT
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP6
D;JEQ
(TRUE_COND6)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP6)
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND7
D;JLT
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP7
D;JEQ
(TRUE_COND7)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP7)
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND8
D;JLT
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP8
D;JEQ
(TRUE_COND8)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP8)
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D-M
@TRUE_COND9
D;JLT
@SP
A=M
M=0
@SP
M=M+1
D=0
@SKIP9
D;JEQ
(TRUE_COND9)
@SP
A=M
M=-1
@SP
M=M+1
(SKIP9)
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D+M
@SP
A=M
M=D
@SP
M=M+1
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@0
D=A-D
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D+M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@0
D=A-D
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D&M
@SP
A=M
M=D
@SP
M=M+1
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
A=M
M=0
@SP
M=M-1
A=M
D=D|M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@0
D=!D
@SP
A=M
M=D
@SP
M=M+1
