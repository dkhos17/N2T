load GameOfLife.asm,
output-file dot.out,
compare-to dot.cmp,
output-list RAM[100]%D1.8.1 RAM[101]%D1.8.1 RAM[102]%D1.8.1 RAM[132]%D1.8.1 RAM[133]%D1.8.1 RAM[134]%D1.8.1 RAM[164]%D1.8.1 RAM[165]%D1.8.1 RAM[166]%D1.8.1;

set PC 0,
set RAM[99] 10,   // set number of generations
set RAM[100] 0,   // set starting pattern
set RAM[101] 1,
set RAM[102] 1,
repeat 10000000 {
  ticktock;
}
output;