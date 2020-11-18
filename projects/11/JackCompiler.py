import sys, os, re

KEYWORDs = ['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
SYMBOLs = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~',]
REPLACEs = {'<' : '&lt;', '>' : '&gt;', '&' : '&amp;'}
OPs = {'+' : 'add','-' : 'sub','*' : 'call Math.multiply 2','/' : 'call Math.divide 2','&' : 'and','|' : 'or','<' : 'lt','>' : 'gt','=' : 'eq'}
UNARY_OPs = {'~' : 'not', '-' : 'neg'}

SYMBOL = 'symbol'
KEYWORD = 'keyword'
IDENTIFIER = 'identifier'
INT_CONST = 'integerConstant' 
STRING_CONST = 'stringConstant'


class JackTokenizer():
    def __init__(self, filename):
        self.code, self.strings, self.integers = self.read(filename)
        # print(self.code)
        self.tokens = self.destroy_code(self.code)
        # print(self.tokens)

    def read(self, filename):
        # read code from jack file
        with open(filename) as file:
            code = file.read()

        # delete comments
        code = re.sub(re.compile("//.+\n|/\*(.|\n)*?\*/"), "", code)
        # code = re.sub(re.compile("/\*.*?\*/"), "", code)

        for symbol in SYMBOLs:
            code = code.replace(symbol, ' ' + symbol + ' ')

        # configure strings
        strings = re.findall(re.compile(r'"(.*)"'), code)
        code = re.sub(re.compile(r'"(.*)"'), STRING_CONST, code)
        # configure integers
        integers = re.findall(re.compile(r"\b[0-9]+\b"), code)
        code = re.sub(re.compile(r"\b[0-9]+\b"), INT_CONST, code)

        return (code.strip(), strings, integers);

    def destroy_code(self, code):
        tokens = []
        for tok in code.split():
            if tok in KEYWORDs:
                tokens.append((tok, KEYWORD))
            elif tok in SYMBOLs:
                tokens.append((tok, SYMBOL))
            elif tok == STRING_CONST:
                tokens.append((self.strings.pop(0), STRING_CONST))
            elif tok == INT_CONST:
                tokens.append((self.integers.pop(0), INT_CONST))
            else:
                tokens.append((tok, IDENTIFIER))

        return tokens

    def hasMoreTokens(self):
        return len(self.tokens) != 0;

    def popNextToken(self):
        # assert self.hasMoreTokens()
        return self.tokens.pop(0)

    def getNextToken(self):
        # assert self.hasMoreTokens()
        return self.tokens[0]

    def pushBackToken(self, token):
        self.tokens.insert(0, token)
    

class JackCompiler():
    def __init__(self, directory):
        self.CLASS_TABLE, self.LOCAL_TABLE = {},{}
        self.field_order, self.static_order = -1,-1
        self.argument_order, self.local_order = -1,-1
        self.if_true_order, self.if_false_order = -1,-1
        self.CLASS_NAME = 'JackCompiler'
        self.compile(directory)

    def compile(self, directory):
        try:
            all, jacks = os.listdir(directory), []
            for fname in all:
                if fname[len(fname)-4:] == 'jack':
                    jacks.append(fname)
                    print("---", fname, "found in a direcotory ---")
            return self.compileDirectory(directory, jacks)
        except:
            if directory[-4:] == 'jack':
                print("---", directory, "found ---")
                return self.compileFile(directory)
            print('no such directory or jack file -___-\n')

    def compileDirectory(self, dir, files):
            for file in files:
                filename = "{}/{}".format(dir, file)
                self.compileFile(filename)
    
    def compileFile(self, filename):        
        tokenizer = JackTokenizer(filename)
        # write code in vm file
        fname = filename[:len(filename)-5] + ".vm"
        with open(fname, 'w') as file:
            if tokenizer.hasMoreTokens():
                self._class_(file, tokenizer)
                print("---", fname, "compiled successfully ---")
   

    def _getKindN_(self, varName):
        if varName in self.CLASS_TABLE:
            return (self.CLASS_TABLE[varName][1], self.CLASS_TABLE[varName][2])
        elif varName in self.LOCAL_TABLE:
            return (self.LOCAL_TABLE[varName][1], self.LOCAL_TABLE[varName][2])
        else: return ("KIND", '#')
    
    def _getType_(self, varName):
        if varName in self.CLASS_TABLE:
            return self.CLASS_TABLE[varName][0]
        elif varName in self.LOCAL_TABLE:
            return self.LOCAL_TABLE[varName][0]
        else: return 'Type'

    def get_order_of_field(self):
        self.field_order += 1
        return self.field_order

    def get_order_of_static(self):
        self.static_order += 1
        return self.static_order

    def get_order_of_argument(self):
        self.argument_order += 1
        return self.argument_order

    def get_order_of_local(self):
        self.local_order += 1
        return self.local_order

    def if_true_label(self):
        self.if_true_order += 1
        return "IF_TRUE{}".format(self.if_true_order)

    def if_false_label(self):
        self.if_false_order += 1
        return "IF_FALSE{}".format(self.if_false_order)


    def _class_(self, file, tokenizer):
        self.CLASS_TABLE = {}
        self.field_order, self.static_order = -1,-1
        # class
        tokenizer.popNextToken()
        # className
        self.CLASS_NAME = self._className_(file, tokenizer)
        # {
        tokenizer.popNextToken()
        # classVarDec
        self._classVarDec_(file, tokenizer)
        # subroutineDec
        self._subroutineDec_(file, tokenizer)
        # }
        tokenizer.popNextToken()


    def _classVarDec_(self, file, tokenizer):
        # ('static'|'field') type varName (',' varName)* ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'static' and xml_body != 'field'): return

        def insert_in_class_table(Name, Kind, Type):
            if Kind == 'field':
               self.CLASS_TABLE[Name] = (Type, 'this', self.get_order_of_field())  
            else:
               self.CLASS_TABLE[Name] = (Type, Kind, self.get_order_of_static())  

        # ('static'|'field')
        Kind = tokenizer.popNextToken()[0]
        # type
        Type = tokenizer.popNextToken()[0]
        # varName
        Name = tokenizer.popNextToken()[0]
        insert_in_class_table(Name, Kind, Type)
        while(tokenizer.getNextToken()[0] != ';'):
            # ,
            tokenizer.popNextToken()
            # varName
            Name = tokenizer.popNextToken()[0]
            insert_in_class_table(Name, Kind, Type)
        # ;
        tokenizer.popNextToken()

        self._classVarDec_(file, tokenizer)

    def _subroutineDec_(self, file, tokenizer):
        # ('constructor'|'function'|'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'constructor' and xml_body != 'function' and xml_body != 'method'): return
        self.LOCAL_TABLE = {}
        self.argument_order, self.local_order = -1,-1
        # ('constructor'|'function'|'method')
        subroutine = tokenizer.popNextToken()[0]
        if subroutine == 'method': self.argument_order += 1
        # ('void' | type)
        tokenizer.popNextToken()
        # subroutineName
        subroutineName = tokenizer.popNextToken()[0]
        # (
        tokenizer.popNextToken()
        # parameterList
        self._parameterList_(file, tokenizer)
        # )
        tokenizer.popNextToken()
        
        # subroutineBody
        self._subroutineBody_(file, subroutine, subroutineName, tokenizer)

        self._subroutineDec_(file, tokenizer)


    
    def _parameterList_(self, file, tokenizer):
        # ((type varName) (',' type varName)*)?
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_body == ')': return 
        
        # type
        Type = tokenizer.popNextToken()[0]
        # varName
        Name = tokenizer.popNextToken()[0]
        self.LOCAL_TABLE[Name] = (Type, 'argument', self.get_order_of_argument())
        while(tokenizer.getNextToken()[0] == ','):
            # ,
            tokenizer.popNextToken()
            # type
            Type = tokenizer.popNextToken()[0]
            # varName
            Name = tokenizer.popNextToken()[0]
            self.LOCAL_TABLE[Name] = (Type, 'argument', self.get_order_of_argument())


    def _subroutineBody_(self, file, subroutine, subroutineName, tokenizer):
        # '{' varDec* statements '}'
        # xml_body, xml_type = tokenizer.getNextToken()
        # if(xml_body != '{'): return

        # {
        tokenizer.popNextToken()
        # varDec
        nVar = self._varDec_(file, tokenizer)
        file.write("function {}.{} {}\n".format(self.CLASS_NAME, subroutineName, nVar))

        if subroutine == 'constructor':
            file.write("push constant {}\n".format(self.get_order_of_field()))
            file.write("call Memory.alloc 1\n")
            file.write("pop pointer 0\n")
        elif subroutine == 'method':
            file.write("push argument 0\n")
            file.write("pop pointer 0\n")

        # statements
        self._statements_(file, tokenizer)
        # }
        tokenizer.popNextToken()
        return nVar

    def _varDec_(self, file, tokenizer):
        # 'var' type varName (',' varName)* ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'var'): return 0
        # var
        tokenizer.popNextToken()       
        # type
        Type = tokenizer.popNextToken()[0]
        # varName
        Name = tokenizer.popNextToken()[0]
        self.LOCAL_TABLE[Name] = (Type, 'local', self.get_order_of_local())       
        nVar = 1
        while(tokenizer.getNextToken()[0] == ','):
            # ,
            tokenizer.popNextToken()
            # varName
            Name = tokenizer.popNextToken()[0]
            self.LOCAL_TABLE[Name] = (Type, 'local', self.get_order_of_local())       
            nVar += 1       
            
        # ;
        tokenizer.popNextToken()       

        return nVar + self._varDec_(file, tokenizer)   

    def _className_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_type != IDENTIFIER): return
        # className
        return tokenizer.popNextToken()[0]

    def _subroutineName_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_type != IDENTIFIER): return
        # subroutineName
        return tokenizer.popNextToken()[0]

    def _varName_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_type != IDENTIFIER): return
        # varName
        return tokenizer.popNextToken()[0]

    def _statements_(self, file, tokenizer):
        # statment*
        while True:
            if not self._statement_(file, tokenizer):
                break
        
    def _statement_(self, file, tokenizer):
        # letStatement | ifStatement | whileStatement | doStatement | returnStatement
        # let        
        if self._letStatement_(file, tokenizer): return True
        # if
        if self._ifStatement_(file, tokenizer): return True
        # while
        if self._whileStatement_(file, tokenizer): return True
        # do
        if self._doStatement_(file, tokenizer): return True
        # return
        if self._returnStatement_(file, tokenizer): return True

        return False


    def _letStatement_(self, file, tokenizer):
        # 'let' varName ('[' expression ']')? '=' expression ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'let'): return False

        # let
        tokenizer.popNextToken()
        # varName
        varName = tokenizer.popNextToken()[0]
        Array = False
        if tokenizer.getNextToken()[0] == '[':
            Kind, N = self._getKindN_(varName)
            file.write("push {} {}\n".format(Kind, N))
            # [
            tokenizer.popNextToken()
            # expression
            self._expression_(file, tokenizer)
            # ]
            tokenizer.popNextToken()
            file.write("add\n")
            Array = True
        # =
        tokenizer.popNextToken()
        # expression
        self._expression_(file, tokenizer)
        # ;
        tokenizer.popNextToken()
        if Array:
            file.write("pop temp 0\n")
            file.write("pop pointer 1\n")
            file.write("push temp 0\n")
            file.write("pop that 0\n")
        else:
            file.write("pop {} {}\n".format(self._getKindN_(varName)[0], self._getKindN_(varName)[1]))
            
        return True


    def _ifStatement_(self, file, tokenizer):
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_body != 'if': return False
        # if
        tokenizer.popNextToken()
        # (
        tokenizer.popNextToken()
        # expression
        self._expression_(file, tokenizer)
        # )
        tokenizer.popNextToken()
        # {
        tokenizer.popNextToken()

        file.write("not\n")
        IF_TRUE, IF_FALSE = self.if_true_label(), self.if_false_label()
        file.write("if-goto {}\n".format(IF_FALSE))

        # statements
        self._statements_(file, tokenizer)
        # }
        tokenizer.popNextToken()
        
        file.write("goto {}\n".format(IF_TRUE))
        file.write("label {}\n".format(IF_FALSE))
        if tokenizer.getNextToken()[0] == 'else':
            # else
            tokenizer.popNextToken()
            # {
            tokenizer.popNextToken()
            # statements
            self._statements_(file, tokenizer)
            # }
            tokenizer.popNextToken()
        file.write("label {}\n".format(IF_TRUE))
        return True

    def _whileStatement_(self, file, tokenizer):
        # 'while' '(' expression ')' '{' statements '}'
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_body != 'while': return False
        
        IF_TRUE, IF_FALSE = self.if_true_label(), self.if_false_label()
        file.write("label {}\n".format(IF_TRUE))

        # while
        tokenizer.popNextToken()
        # (
        tokenizer.popNextToken()
        # expression
        self._expression_(file, tokenizer)
        # )
        tokenizer.popNextToken()
        # {
        tokenizer.popNextToken()

        file.write("not\n")
        file.write("if-goto {}\n".format(IF_FALSE))

        # statements
        self._statements_(file, tokenizer)
        # }
        tokenizer.popNextToken()
        file.write("goto {}\n".format(IF_TRUE))
        file.write("label {}\n".format(IF_FALSE))
        return True
    
    def _doStatement_(self, file, tokenizer):
        # 'do' subroutineCall ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_body != 'do': return False

        # do
        tokenizer.popNextToken()
        # subroutineCall
        self._subroutineCall_(file, tokenizer);
        # ;
        tokenizer.popNextToken()
        file.write("pop temp 0\n")
        return True

    def _returnStatement_(self, file, tokenizer):
        # 'return' expression? ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_body != 'return': return False

        # return
        tokenizer.popNextToken()
        # void
        if tokenizer.getNextToken()[0] == ';':
            file.write("push constant 0\n")
        else:
            # expression
            self._expression_(file, tokenizer)
        # ;
        tokenizer.popNextToken()
        file.write("return\n")
        return True

    def _expression_(self, file, tokenizer):
        # term (op term)*
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_type != INT_CONST and xml_type != STRING_CONST and xml_type != KEYWORD and xml_type != IDENTIFIER and xml_body != '(' and xml_body not in UNARY_OPs:
            return False
        # term
        self._term_(file, tokenizer)
        # (op term)*
        while tokenizer.getNextToken()[0] in OPs:
            # op
            op = OPs[tokenizer.popNextToken()[0]]
            # term
            self._term_(file, tokenizer)
            file.write(op + '\n')
        return True


    def _term_(self, file, tokenizer):
        # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        xml_body, xml_type = tokenizer.popNextToken()
        # integerConstant | stringConstant | keywordConstant
        if xml_type == INT_CONST or xml_type == STRING_CONST or xml_type == KEYWORD:
            if xml_body == 'this':
                return file.write("push pointer 0\n")
            if xml_body == 'false' or xml_body == 'null':
                return file.write("push constant 0\n")
            if xml_body == 'true':
                return file.write("push constant 1\nneg\n")
            if xml_type == STRING_CONST:
                file.write("push constant {}\n".format(len(xml_body)))
                file.write("call String.new 1\n")
                for ch in xml_body:
                    file.write("push constant {}\n".format(ord(ch)))
                    file.write("call String.appendChar 2\n")
                return
            return file.write("push constant {}\n".format(xml_body))

        #  varName | varName '[' expression ']' | subroutineCall
        elif xml_type == IDENTIFIER:
            # subroutineCall
            if tokenizer.getNextToken()[0] == '(' or tokenizer.getNextToken()[0] == '.':
                tokenizer.pushBackToken((xml_body, xml_type))
                self._subroutineCall_(file, tokenizer)

            # varName | varName '[' expression ']'
            else:
                tokenizer.pushBackToken((xml_body, xml_type))
                # varName
                varName = self._varName_(file, tokenizer)
                Kind, N = self._getKindN_(varName)
                file.write("push {} {}\n".format(Kind, N))
                # '[' expression ']'
                if tokenizer.getNextToken()[0] == '[':
                    # [
                    tokenizer.popNextToken()
                    # expression
                    self._expression_(file, tokenizer)
                    # ]
                    tokenizer.popNextToken()
                    file.write("add\npop pointer 1\npush that 0\n")

        # '(' expression ')'
        elif xml_body == '(':
            # (
            # self.write_in_xml(file, (xml_body, xml_type))
            # expression
            self._expression_(file, tokenizer)
            # )
            tokenizer.popNextToken()

        # unaryOp term
        elif xml_body in UNARY_OPs:
            # unaryOp
            # self.write_in_xml(file, (xml_body, xml_type))
            uOP = UNARY_OPs[xml_body]
            # term
            self._term_(file, tokenizer)
            file.write(uOP + '\n')


    def _subroutineCall_(self, file, tokenizer):
        # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        xml_body, xml_type = tokenizer.popNextToken()
        if xml_type != IDENTIFIER and xml_type != SYMBOL: return False

        className, nVar = '', 0
        if tokenizer.getNextToken()[0] == '.':
            # className | varName
            className = xml_body
            # .
            tokenizer.popNextToken()
            # subroutineName
            subroutineName = self._subroutineName_(file, tokenizer)
            # if varName, than its method and we need to push this
            if className in self.LOCAL_TABLE or className in self.CLASS_TABLE:
                file.write("push {} {}\n".format(self._getKindN_(className)[0], self._getKindN_(className)[1]))
                className = self._getType_(className)
                nVar += 1
            className += '.'
            
        else:
            # subroutineName
            # self.write_in_xml(file, (xml_body, xml_type))
            className = self.CLASS_NAME + '.'
            subroutineName = xml_body
            file.write("push pointer 0\n")
            nVar += 1

        # (
        tokenizer.popNextToken()
        # expressionList
        nVar += self._expressionList_(file, tokenizer)
        # )
        tokenizer.popNextToken()
        file.write("call {}{} {}\n".format(className, subroutineName, nVar))
        return True
    
    def _expressionList_(self, file, tokenizer):
        # (expression (',' expression)* )?
        # expression
        nVar = 0
        if self._expression_(file, tokenizer):
            nVar = 1
        # (',' expression)* )?
        while tokenizer.getNextToken()[0] == ',':
            # ,
            tokenizer.popNextToken()
            # expression
            self._expression_(file, tokenizer)
            nVar += 1
        return nVar

if __name__ == '__main__':
    assert len(sys.argv) == 2 # -> python3 JackCompiler.py Dir or File
    JackCompiler(sys.argv[1:][0])