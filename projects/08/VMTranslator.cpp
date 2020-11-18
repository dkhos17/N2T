#include"VMTranslator.h"
using namespace std;

int uniq = 0;
map<string, string> ARITHMETICs = {{"add","M=D+M"},{"sub","M=M-D"}, {"neg","M=-M"},{"eq","D;JEQ"},{"gt","D;JGT"},{"lt","D;JLT"},{"and","M=D&M"},{"or","M=D|M"},{"not","M=!M"}};
map<string, string> MEMORYs = {{"push","PUSH"},{"pop","POP"}}, SEGMENTs = {{"local","LCL"},{"argument","ARG"},{"this","THIS"},{"that","THAT"},{"temp","R5"},{"pointer0","THIS"},{"pointer1","THAT"}};
map<string, string> BRANCHINGs = {{"label","LABEL"},{"goto","GOTO"},{"if-goto","IF-GOTO"}};
map<string, string> FUNCTIONs = {{"function", "func"}};
/* ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- */

/* translates arithemtic access commands */
string VM_Arithmetic(string& fname, string& line) {
    auto IFT = LABEL("IF_TRUE", uniq), IFF = LABEL("IF_FALSE", uniq);
    if(line == "eq" || line == "gt" || line == "lt")
        return uniq++, JBASE_TRUE(IFT) + ARITHMETICs[line] + "\n" + JBASE_FALSE(IFF) + JBASE_CHECK(IFT,IFF); 
    
    return uniq++, (line[0] == 'n' ? NBASE : BASE) + ARITHMETICs[line] + "\n";
}

/* return push's bodys - loads *addr in D, where *addr = *(segmentPointer+i) */
string push_body(string& fname, string segment, string i) {
    if(segment == "static") return "@"+fname+i+"\nD=M\n";
    if(segment == "pointer") return "@"+SEGMENTs[segment+i]+"\nD=M\n";

    auto addr = "@"+i+"\nD=A\n";
    if(SEGMENTs.count(segment))
        return addr + "@"+SEGMENTs[segment]+"\nD=D+"+((segment == "temp") ? "A\n" : "M\n") + "A=D\nD=M\n";
    return addr;
}

/* return pop's bodys - loads *addr in D, where *addr = *(segmentPointer+i) */
string pop_body(string& fname, string segment, string i) {
    if(segment == "static") return "@"+fname+i+"\n";
    if(segment == "pointer") return "@"+SEGMENTs[segment+i]+"\n";
    
    auto addr = "@"+i+"\nD=A\n";
    return addr+"@"+SEGMENTs[segment]+"\nD=D+"+((segment == "temp") ? "A\n" : "M\n");
}

/* translates memory access commands */    
string VM_Memory(string& fname, string& line) {
    auto [popush, segment, i] = get_tokens(line);

    if(popush == "push")
        return push_body(fname, segment, i) + PUSH_TAIL;
    return POP_HEAD + pop_body(fname, segment, i) + POP_TAIL(segment);
}

/* translates branch access commands */
string VM_Branching(string& fname, string& line) {
    auto [command, label, _] = get_tokens(line);
    if(command == "label") return LABEL("("+label+")\n", -1);
    if(command == "goto") return LABEL("@"+label, -1) + GOTO_TAIL;
    return IFGOTO_HEAD + LABEL("@"+label, -1) + IFGOTO_TAIL;
}

string call(string func, string n) {
    auto call_head = PUSH_retAddr(LABEL("RETADDR",uniq))+PUSH("LCL")+PUSH("ARG")+PUSH("THIS")+PUSH("THAT");
    auto call_tail = nArgs(n)+LABEL("@"+func,-1)+GOTO_TAIL+LABEL("(RETADDR",uniq)+")\n";
    return uniq++, call_head+call_tail;
}

string VM_Function(string& fname, string& line) {
    auto [command, func, n] = get_tokens(line);
    if(command == "function") {
        func = "("+func+")\n"+(n!="0"?"@SP\nA=M\n":"");
        for(int i = 0; i < stoi(n); i++) 
            func += push_body(fname, "constant", "0")+PUSH_TAIL;
        return func;
    }
    if(command == "call") 
        return call(func, n);
    return RETURN;
}

/* if line is a vm-code trims additional chars and returns true, or  returns false*/  
int is_line(string& line, bool debug = false) {
    if(line.size() && int(line.back()) == 13) line.pop_back(); // delete CR charachter
    if(line.find('/') != string::npos) // delete comments
        line = line.substr(0, line.find('/'));

    auto s = line.find_first_not_of(' '), e = line.find_last_not_of(' ');
    if(s == string::npos || e == string::npos) return 0; // not a code

    line = line.substr(s,e-s+1);
    if(debug) cout << "// "<< line << endl;

    auto tok = line.substr(0, line.find(' '));
    return (MEMORYs.count(tok) ? MEMORY : (ARITHMETICs.count(tok) ? ARITHMETIC : (BRANCHINGs.count(tok) ? BRANCHING : FUNCTION)));
}

int main(int argc, char** argv) {
    assert(argc == 2); // check if arguments contains file dir.
    auto fout = string(argv[1])+string(argv[1]).substr(string(argv[1]).rfind("/"));
    freopen((fout + ".asm").c_str(), "w", stdout);
    
    for(auto& fname : vm_files(argv[1])) {
        ifstream vmfile((string(argv[1])+"/"+fname+"vm").c_str());

        string line;    
        while(getline(vmfile, line)) {
            switch(is_line(line, true)) {
                case ARITHMETIC: cout << VM_Arithmetic(fname,line) << endl; break;
                case MEMORY: cout << VM_Memory(fname,line) << endl; break;
                case BRANCHING: cout << VM_Branching(fname,line) << endl; break;
                case FUNCTION: cout << VM_Function(fname,line) << endl; break;
                default: break; // line isn't such a code.
            }
        }
    }
    return 0;
}