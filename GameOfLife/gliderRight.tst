load GameOfLife.asm,
output-file gliderRight.out,
compare-to gliderRight.cmp,
output-list RAM[496]%D1.8.1 RAM[497]%D1.8.1 RAM[498]%D1.8.1 RAM[528]%D1.8.1 RAM[529]%D1.8.1 RAM[530]%D1.8.1 RAM[560]%D1.8.1 RAM[561]%D1.8.1 RAM[562]%D1.8.1;

set PC 0,
set RAM[99] 48,   // set number of generations
set RAM[100] 0,   // set starting pattern
set RAM[101] 1,
set RAM[102] 0,
set RAM[132] 0,
set RAM[133] 0,
set RAM[134] 1,
set RAM[164] 1,
set RAM[165] 1,
set RAM[166] 1,
repeat 10000000 {
  ticktock;
}
output;