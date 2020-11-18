import sys, os, re

KEYWORDs = ['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
SYMBOLs = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~',]
REPLACEs = {'<' : '&lt;', '>' : '&gt;', '&' : '&amp;'}
OPs = ['+','-','*','/','&','|','<','>','=']
UNARY_OPs = ['~','-']

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
    

class JackAnalyzer():
    def __init__(self, directory):
        files = self.get_files(directory)
        self.tokenize(directory + '/', files)
        self.analyze(directory + '/', files);

    def get_files(self, directory):
        all, jacks = os.listdir(directory), []
        for fname in all:
            if fname[len(fname)-4:] == 'jack':
                jacks.append(fname)
                print("---", fname, "found in a direcotory ---")
        return jacks

    def write_in_xml(self, xml_file, xml_args):
        xml_body, xml_type = xml_args
        if xml_body in REPLACEs:
            xml_body = REPLACEs[xml_body]
        xml_file.write(f'<{xml_type}> {xml_body} </{xml_type}>\n')

    def tokenize(self, dir, files):
        for filename in files:
            tokenizer = JackTokenizer(dir + filename)
            # write code in xml file
            fname = dir + filename[:len(filename)-5] + "Tokens.xml"
            with open(fname, 'w') as file:
                file.write('<tokens> \n')
                while(tokenizer.hasMoreTokens()):
                    self.write_in_xml(file, tokenizer.popNextToken())
                file.write('</tokens> \n')
                print("---", fname, "tokenized successfully in a direcotory ---")

    def analyze(self, dir, files):
        for filename in files:
            tokenizer = JackTokenizer(dir + filename)
            # write code in xml file
            fname = dir + filename[:len(filename)-5] + "Analyze.xml"
            with open(fname, 'w') as file:
                if tokenizer.hasMoreTokens():
                    self._class_(file, tokenizer)
                    print("---", fname, "analyzed successfully in a direcotory ---")


    def _class_(self, file, tokenizer):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        file.write(f'<class>\n')
        # class
        self.write_in_xml(file, tokenizer.popNextToken())
        # className
        self._className_(file, tokenizer)
        # {
        self.write_in_xml(file, tokenizer.popNextToken())
        # classVarDec
        self._classVarDec_(file, tokenizer)
        # subroutineDec
        self._subroutineDec_(file, tokenizer)
        # }
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write('</class>\n')

    def _classVarDec_(self, file, tokenizer):
        # ('static'|'field') type varName (',' varName)* ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'static' and xml_body != 'field'): return
        file.write(f'<classVarDec>\n')

        # ('static'|'field')
        self.write_in_xml(file, tokenizer.popNextToken())
        # type
        self.write_in_xml(file, tokenizer.popNextToken())
        # varName
        self.write_in_xml(file, tokenizer.popNextToken())
        while(tokenizer.getNextToken()[0] != ';'):
            # ,
            self.write_in_xml(file, tokenizer.popNextToken())
            # varName
            self.write_in_xml(file, tokenizer.popNextToken())
        # ;
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</classVarDec>\n')
        self._classVarDec_(file, tokenizer)

    def _subroutineDec_(self, file, tokenizer):
        # ('constructor'|'function'|'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'constructor' and xml_body != 'function' and xml_body != 'method'): return
        file.write(f'<subroutineDec>\n')
        
        # ('constructor'|'function'|'method')
        self.write_in_xml(file, tokenizer.popNextToken())
        # ('void' | type)
        self.write_in_xml(file, tokenizer.popNextToken())
        # subroutineName
        self.write_in_xml(file, tokenizer.popNextToken())
        # (
        self.write_in_xml(file, tokenizer.popNextToken())
        # parameterList
        self._parameterList_(file, tokenizer)
        # )
        self.write_in_xml(file, tokenizer.popNextToken())
        # subroutineBody
        self._subroutineBody_(file, tokenizer)

        file.write(f'</subroutineDec>\n')
        self._subroutineDec_(file, tokenizer)


    
    def _parameterList_(self, file, tokenizer):
        # ((type varName) (',' type varName)*)?
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'int' and xml_body != 'boolean' and xml_body != 'char'): 
            return file.write(f'<parameterList>\n'), file.write(f'</parameterList>\n');
        
        file.write(f'<parameterList>\n')
        # type
        self.write_in_xml(file, tokenizer.popNextToken())
        # varName
        self.write_in_xml(file, tokenizer.popNextToken())
        while(tokenizer.getNextToken()[0] == ','):
            # ,
            self.write_in_xml(file, tokenizer.popNextToken())
            # type
            self.write_in_xml(file, tokenizer.popNextToken())
            # varName
            self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</parameterList>\n')

    def _subroutineBody_(self, file, tokenizer):
        # '{' varDec* statements '}'
        # xml_body, xml_type = tokenizer.getNextToken()
        # if(xml_body != '{'): return
        file.write(f'<subroutineBody>\n')

        # {
        self.write_in_xml(file, tokenizer.popNextToken())
        # varDec
        self._varDec_(file, tokenizer)
        # statements
        self._statements_(file, tokenizer)
        # }
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</subroutineBody>\n')

    def _varDec_(self, file, tokenizer):
        # 'var' type varName (',' varName)* ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'var'): return
        file.write(f'<varDec>\n')
        # var
        self.write_in_xml(file, tokenizer.popNextToken())
        # type
        self.write_in_xml(file, tokenizer.popNextToken())
        # varName
        self.write_in_xml(file, tokenizer.popNextToken())

        while(tokenizer.getNextToken()[0] == ','):
            # ,
            self.write_in_xml(file, tokenizer.popNextToken())
            # varName
            self.write_in_xml(file, tokenizer.popNextToken())
        # ;
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</varDec>\n')
        self._varDec_(file, tokenizer)   

    def _className_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_type != IDENTIFIER): return False
        # className
        self.write_in_xml(file, tokenizer.popNextToken())
        return True

    def _subroutineName_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_type != IDENTIFIER): return False
        # subroutineName
        self.write_in_xml(file, tokenizer.popNextToken())
        return True

    def _varName_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_type != IDENTIFIER): return False
        # varName
        self.write_in_xml(file, tokenizer.popNextToken())
        return True

    def _statements_(self, file, tokenizer):
        # statment*
        file.write(f'<statements>\n')
        while True:
            if not self._statement_(file, tokenizer):
                break
        file.write(f'</statements>\n')
        
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
        file.write(f'<letStatement>\n')

        # let
        self.write_in_xml(file, tokenizer.popNextToken())
        # varName
        self.write_in_xml(file, tokenizer.popNextToken())

        if tokenizer.getNextToken()[0] == '[':
            # [
            self.write_in_xml(file, tokenizer.popNextToken())
            # expression
            self._expression_(file, tokenizer)
            # ]
            self.write_in_xml(file, tokenizer.popNextToken())

        # =
        self.write_in_xml(file, tokenizer.popNextToken())
        # expression
        self._expression_(file, tokenizer)
        # ;
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</letStatement>\n')
        return True


    def _ifStatement_(self, file, tokenizer):
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'if'): return False
        file.write(f'<ifStatement>\n')
        # if
        self.write_in_xml(file, tokenizer.popNextToken())
        # (
        self.write_in_xml(file, tokenizer.popNextToken())
        # expression
        self._expression_(file, tokenizer)
        # )
        self.write_in_xml(file, tokenizer.popNextToken())
        # {
        self.write_in_xml(file, tokenizer.popNextToken())
        # statements
        self._statements_(file, tokenizer)
        # }
        self.write_in_xml(file, tokenizer.popNextToken())

        if(tokenizer.getNextToken()[0] == 'else'):
            # else
            self.write_in_xml(file, tokenizer.popNextToken())
            # {
            self.write_in_xml(file, tokenizer.popNextToken())
            # statements
            self._statements_(file, tokenizer)
            # }
            self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</ifStatement>\n')
        return True

    def _whileStatement_(self, file, tokenizer):
        # 'while' '(' expression ')' '{' statements '}'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'while'): return False
        file.write(f'<whileStatement>\n')

        # while
        self.write_in_xml(file, tokenizer.popNextToken())
        # (
        self.write_in_xml(file, tokenizer.popNextToken())
        # expression
        self._expression_(file, tokenizer)
        # )
        self.write_in_xml(file, tokenizer.popNextToken())
        # {
        self.write_in_xml(file, tokenizer.popNextToken())
        # statements
        self._statements_(file, tokenizer)
        # }
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</whileStatement>\n')
        return True
    
    def _doStatement_(self, file, tokenizer):
        # 'do' subroutineCall ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'do'): return False
        file.write(f'<doStatement>\n')

        # do
        self.write_in_xml(file, tokenizer.popNextToken())
        # subroutineCall
        self._subroutineCall_(file, tokenizer);
        # ;
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</doStatement>\n')
        return True

    def _returnStatement_(self, file, tokenizer):
        # 'return' expression? ';'
        xml_body, xml_type = tokenizer.getNextToken()
        if(xml_body != 'return'): return False
        file.write(f'<returnStatement>\n')

        # return
        self.write_in_xml(file, tokenizer.popNextToken())
        # expression
        self._expression_(file, tokenizer)
        # ;
        self.write_in_xml(file, tokenizer.popNextToken())

        file.write(f'</returnStatement>\n')
        return True

    def _expression_(self, file, tokenizer):
        xml_body, xml_type = tokenizer.getNextToken()
        if xml_type != INT_CONST and xml_type != STRING_CONST and xml_type != KEYWORD and xml_type != IDENTIFIER and xml_body != '(' and xml_body not in UNARY_OPs:
            return
        # term (op term)*
        file.write(f'<expression>\n')
        # term
        self._term_(file, tokenizer)
        # (op term)*
        while tokenizer.getNextToken()[0] in OPs:
            # op
            self.write_in_xml(file, tokenizer.popNextToken())
            # term
            self._term_(file, tokenizer)
        
        file.write(f'</expression>\n')


    def _term_(self, file, tokenizer):
        # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        xml_body, xml_type = tokenizer.popNextToken()
        file.write(f'<term>\n')
        # integerConstant | stringConstant | keywordConstant
        if xml_type == INT_CONST or xml_type == STRING_CONST or xml_type == KEYWORD:
            self.write_in_xml(file, (xml_body, xml_type))

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
                self._varName_(file, tokenizer)
                # '[' expression ']'
                if tokenizer.getNextToken()[0] == '[':
                    # [
                    self.write_in_xml(file, tokenizer.popNextToken())
                    # expression
                    self._expression_(file, tokenizer)
                    # ]
                    self.write_in_xml(file, tokenizer.popNextToken())

        # '(' expression ')'
        elif xml_body == '(':
            # (
            self.write_in_xml(file, (xml_body, xml_type))
            # expression
            self._expression_(file, tokenizer)
            # )
            self.write_in_xml(file, tokenizer.popNextToken())

        # unaryOp term
        elif xml_body in UNARY_OPs:
            # unaryOp
            self.write_in_xml(file, (xml_body, xml_type))
            # term
            self._term_(file, tokenizer)
        file.write(f'</term>\n')

    
    def _subroutineCall_(self, file, tokenizer):
        # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        xml_body, xml_type = tokenizer.popNextToken()
        if xml_type != IDENTIFIER and xml_type != SYMBOL: return False
        # file.write(f'<subroutineCall>\n')
        if tokenizer.getNextToken()[0] == '.':
            # className | varName
            self.write_in_xml(file, (xml_body, xml_type))
            # .
            self.write_in_xml(file, tokenizer.popNextToken())
            # subroutineName
            self._subroutineName_(file, tokenizer)
        else :
            # subroutineName
            self.write_in_xml(file, (xml_body, xml_type))

        # (
        self.write_in_xml(file, tokenizer.popNextToken())
        # expressionList
        self._expressionList_(file, tokenizer)
        # )
        self.write_in_xml(file, tokenizer.popNextToken())

        # file.write(f'</subroutineCall>\n')
        return True
    
    def _expressionList_(self, file, tokenizer):
        # (expression (',' expression)* )?
        file.write(f'<expressionList>\n')
        # expression
        self._expression_(file, tokenizer)
        # (',' expression)* )?
        while tokenizer.getNextToken()[0] == ',':
            # ,
            self.write_in_xml(file, tokenizer.popNextToken())
            # expression
            self._expression_(file, tokenizer)
        
        file.write(f'</expressionList>\n')

if __name__ == '__main__':
    JackAnalyzer(sys.argv[1:][0])