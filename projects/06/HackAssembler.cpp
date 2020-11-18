#include <bits/stdc++.h>
using namespace std;
#define SCREEN 16384
#define KBD 24576

int line_num = 0, ADDRESS = 16;
map<string, int> RAM = {{"SP",0}, {"LCL",1}, {"ARG",2}, {"THIS",3}, {"THAT",4}, {"KBD",KBD}, {"SCREEN",SCREEN}, {"R0",0}, {"R1",1},
{"R2",2}, {"R3",3}, {"R4",4}, {"R5",5}, {"R6",6}, {"R7",7}, {"R8",8}, {"R9",9}, {"R10",10}, {"R11",11}, {"R12",12}, {"R13",13}, {"R14",14},{"R15",15},{"R16",16}};
map<string, string> DESTs = {{"null","000"}, {"M","001"}, {"D","010"}, {"MD","011"}, {"A","100"}, {"AM","101"}, {"AD","110"}, {"AMD","111"}};
map<string, string> JUMPs = {{"null","000"}, {"JGT","001"}, {"JEQ","010"}, {"JGE","011"}, {"JLT","100"}, {"JNE","101"}, {"JLE","110"}, {"JMP","111"}};
map<string, string> COMPs = {{"A","0110000"}, {"A+1","0110111"}, {"D+1","0011111"}, {"A-D","0000111"}, {"M-1","1110010"}, {"D-M","1010011"}, {"M-D","1000111"}, {"D&M","1000000"}, 
{"D+M","1000010"}, {"D|M","1010101"}, {"!D","0001101"}, {"-D","0001111"}, {"M+1","1110111"}, {"A-1","0110010"}, {"D|A","0010101"}, {"1","0111111"}, {"D+A","0000010"}, {"-A","0110011"}, 
{"0","0101010"}, {"-1","0111010"}, {"D-A","0010011"}, {"!M","1110001"}, {"-M","1110011"}, {"D-1","0001110"}, {"!A","0110001"}, {"M","1110000"}, {"D","0001100"}, {"D&A","0000000"}};
/* ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- */
/* returns A instruction 16bit as a string */
string A_instruction(string& line) {
    string symbol = line.substr(1,line.size());
    if(isdigit(symbol[0]) && !RAM.count(symbol))  // check variable as number.
        RAM[symbol] = stoi(symbol);
    else if(!RAM.count(symbol)) // check variable as string.
        RAM[symbol] = ADDRESS++;

    return bitset<16UL>(RAM[symbol]).to_string();
}

/* returns C instruction 16bit as a string */
string C_instruction(string& line) {
    auto eq = line.find('='), brk = line.find(';');
    if(eq != string::npos) // =
        return "111" + COMPs[line.substr(eq+1)] + DESTs[line.substr(0,eq)] + JUMPs["null"];
    return "111" + COMPs[line.substr(0,brk)] + DESTs["null"] + JUMPs[line.substr(brk+1)];
}

/* if line is a asm-code trims additional chars and returns true, or checks if line is a label and returns false*/  
int is_line(string& line) {
    if(line.size() && int(line.back()) == 13) line.pop_back(); // delete CR charachter
    if(line.find('/') != string::npos) // delete comments
        line = line.substr(0, line.find('/'));

    auto s = line.find_first_not_of(' '), e = line.find_last_not_of(' ');
    if(s == string::npos || e == string::npos) return 0; // not a code
    
    if(line[s] == '(' && line[e] == ')') // recognize LABEL
        return RAM[line.substr(s+1, e-s-1)] = line_num, 0;
        
    line = line.substr(s,e-s+1); // trim white spaces
    return line.empty() ? 0 : ++line_num;
}

int main(int argc, char** argv) {
    assert(argc == 3); // check -> ./a.out path/xxx.asm path/xxx.hack
    freopen(argv[1], "r", stdin);
    freopen(argv[2], "w", stdout);

    string line;
    vector<string> code_lines; 
    while(getline(cin, line)) 
        if(is_line(line)) code_lines.push_back(line);
    
    for(auto code : code_lines) 
        cout << ((code[0]== '@') ? A_instruction(code) : C_instruction(code)) << endl;
    return 0;
}