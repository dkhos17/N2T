#include<bits/stdc++.h>
#include <sys/types.h>
#include <dirent.h>
using namespace std;
#define ARITHMETIC 1
#define MEMORY 2
#define BRANCHING 3
#define FUNCTION 4

#define _INIT_ "@261\nD=A\n@SP\nM=D\n" // call("Sys.init", "0")

#define LABEL(label,uniq) string(label)+(uniq == -1 ? "" : to_string(uniq))

#define PUSH_TAIL "@SP\nA=M\nM=D\n@SP\nM=M+1\n"
#define POP_HEAD  "@SP\nM=M-1\nA=M\nD=M\n"
#define POP_TAIL(segment) (segment != "static" && segment != "pointer" ? "@saveD\nM=D\n@SP\nA=M\nD=M\n@saveD\nA=M\nM=D\n" : "M=D\n")

#define BASE "@SP\nAM=M-1\nD=M\nA=A-1\n"
#define NBASE "@SP\nA=M-1\n"
#define JBASE_TRUE(IF_TRUE) "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@"+string(IF_TRUE)+"\n"
#define JBASE_FALSE(IF_FALSE) "@SP\nA=M-1\nM=0\n@"+string(IF_FALSE)+"\n"
#define JBASE_CHECK(IF_TRUE,IF_FALSE) "0;JMP\n("+string(IF_TRUE)+")\n@SP\nA=M-1\nM=-1\n("+string(IF_FALSE)+")\n"

#define GOTO_TAIL "\n0;JMP\n"
#define IFGOTO_TAIL "\nD;JNE\n"
#define IFGOTO_HEAD "@SP\nAM=M-1\nD=M\n"

#define Var "M=0\nA=A+1\n"
#define PUSH_retAddr(label) "@"+string(label)+"\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
#define PUSH(label) "@"+string(label)+"\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
#define nArgs(n) "@SP\nD=M\n@5\nD=D-A\n@"+n+"\nD=D-A\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n"

//same here, but parts separated ->  #define RETURN "@LCL\nD=M\n@endFrame\nM=D\n" + "@5\nA=D-A\nD=M\n@retAddr\nM=D\n" + "@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n" + "@ARG\nD=M+1\n@SP\nM=D\n" + "@LCL\nAM=M-1\nD=M\n@THAT\nM=D\n" + "@LCL\nAM=M-1\nD=M\n@THIS\nM=D\n" + "@LCL\nAM=M-1\nD=M\n@ARG\nM=D\n" + "@LCL\nAM=M-1\nD=M\n@LCL\nM=D\n" + "@retAddr\nA=M\n0;JMP\n" 
#define RETURN "@LCL\nD=M\n@endFrame\nM=D\n@5\nA=D-A\nD=M\n@retAddr\nM=D\n@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n@LCL\nAM=M-1\nD=M\n@THAT\nM=D\n@LCL\nAM=M-1\nD=M\n@THIS\nM=D\n@LCL\nAM=M-1\nD=M\n@ARG\nM=D\n@LCL\nAM=M-1\nD=M\n@LCL\nM=D\n@retAddr\nA=M\n0;JMP\n" 

/* splits line on whitespace and returns tokens. (max token num = 3) */
tuple<string,string,string> get_tokens(string& line) {
    auto tok1 = line.substr(0, line.find(' '));
    auto tok3 = line.substr(line.find(' ')+1);
    auto tok2 = tok3.substr(0, tok3.find(' '));
    return make_tuple(tok1, tok2, tok3.substr(tok3.find(' ')+1));
}

/* returns list of vmfile names + "." */
vector<string> vm_files(const char *path) {
    struct dirent *entry;
    DIR *dir = opendir(path);

    assert(dir != NULL);
    vector<string> vms;
    
    while ((entry = readdir(dir)) != NULL) 
        if(string(entry->d_name).find(".vm") != string::npos) 
            vms.push_back(string(entry->d_name).substr(0,string(entry->d_name).size()-2));
    
    closedir(dir);

    auto sys = find(vms.begin(), vms.end(), "Sys.");
    if(sys != vms.end()) {
        cout << _INIT_ << endl;
        swap(vms[0], vms[sys-vms.begin()]);
    }
    
    return vms;
}