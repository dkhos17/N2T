load GameOfLife.asm,
output-file gliderLeft.out,
compare-to gliderLeft.cmp,
output-list RAM[132]%D1.8.1 RAM[133]%D1.8.1 RAM[134]%D1.8.1 RAM[164]%D1.8.1 RAM[165]%D1.8.1 RAM[166]%D1.8.1 RAM[196]%D1.8.1 RAM[197]%D1.8.1 RAM[198]%D1.8.1;

set PC 0,
set RAM[99] 4,   // set number of generations
set RAM[100] 0,   // set starting pattern
set RAM[101] 1,
set RAM[102] 0,
set RAM[132] 1,
set RAM[133] 0,
set RAM[134] 0,
set RAM[164] 1,
set RAM[165] 1,
set RAM[166] 1,
repeat 10000000 {
  ticktock;
}
output;