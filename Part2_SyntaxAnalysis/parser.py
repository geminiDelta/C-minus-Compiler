# parser.py
# Written by: Austin Green
# Description: Parser for Compilers course

import re
from sys import argv, exit


# CLASSES
class Token:
    def __init__(self, tokType, tokVal):
        self.tokType = tokType
        self.tokVal = tokVal


# LA FUNCTIONS
def resetFlags():
    """Reset all flags to False"""
    for flag in flags:
        flags[flag] = False


def setFlag(tokenChar):
    """Set a flag based on input"""
    resetFlags()  # set all flags to False
    if tokenChar is None:
        return None
    if re.match(r'[a-z]', tokenChar):  # if letter
        flags["letterFlag"] = True  # set letter flag
    elif re.match(r'\d', tokenChar):  # if number
        flags["numberFlag"] = True  # set number flag
    elif tokenChar in allSymbols or \
            tokenChar == "!":  # if symbol
        flags["symbolFlag"] = True  # set symbol flag
    elif re.match(r'\s', tokenChar):  # if whitespace
        flags["whitespaceFlag"] = True  # set ws flag
    else:  # otherwise, invalid character
        flags["errorFlag"] = True  # set error flag


def flagSet():
    """Return true if a flag is set; False otherwise"""
    for flag in flags:
        if flags[flag]:
            return True
    return False


# LA VARIABLES
# Analyzer variables
tokenList = []
keywords = ("else", "if", "int", "float", "return", "void", "while")
allSymbols = ("+", "-", "*", "/", "<", "<=", ">=", ">", "==", "!=", "=", ";", ",", "(", ")", "[", "]", "{", "}")
finSymbols = ("+", "-", "<=", ">=", "==", "!=", ";", ",", "(", ")", "[", "]", "{", "}")
lineNum = 0
# Scanning variables
commentDepth = 0
currToken = ""
flags = {"symbolFlag": False, "letterFlag": False, "numberFlag": False, "whitespaceFlag": False, "errorFlag": False}

# PROGRAM
try:
    f = open(argv[1], 'r')  # open argument file
    for line in f:  # read each line of file
        lineNum += 1
        line = line.rstrip()
        # print input line if not blank
        # if len(line) > 0:
        #     print "INPUT(" + str(lineNum) + "): " + line  # display input line
        # scan line (iterator)
        lineIter = iter(line)  # initialize iterator for line
        c = ""
        while c is not None:  # while line has more characters
            if commentDepth > 0:  # if in block comment
                c = next(lineIter, None)
                if c != "/" and c != "*":  # if c not comment character
                    currToken = ""  # clear token
                    continue  # move on
                # look for /*
                elif currToken + c == "/*":
                    commentDepth += 1  # increment comment depth
                    currToken = ""  # reset token
                # look for */
                elif currToken + c == "*/":
                    commentDepth -= 1  # decrement comment depth
                    currToken = ""  # reset token
                else:  # "/" or "*"
                    currToken = c
            elif flags["letterFlag"]:  # if letter flagged
                while c is not None and re.match(r'[a-z]', c):
                    currToken += c
                    c = next(lineIter, None)
                # check if token is keyword
                if currToken in keywords:
                    tokenList.append(Token('keyword', currToken))
                    # print "keyword: " + currToken
                    currToken = ""
                    setFlag(c)
                # otherwise, token is an ID
                else:
                    tokenList.append(Token('ID', currToken))
                    # print "ID: " + currToken
                    currToken = ""
                    setFlag(c)
            elif flags["numberFlag"]:  # if number flagged
                isFloat = False
                isSciNotation = False
                while c is not None and \
                        (re.match(r'\d', c) or
                         (c == "." and not isFloat and not isSciNotation) or
                         (c == "E" and not isSciNotation)):
                    if c == ".":
                        isFloat = True
                    elif c == "E":
                        isSciNotation = True
                    currToken += c
                    c = next(lineIter, None)
                    if currToken[-1] == "E" and (c == "+" or c == "-"):
                        currToken += c
                        c = next(lineIter, None)
                # if trailing character not "." print number, otherwise print error
                if currToken[-1] in (".", "E", "+", "-"):
                    # print "REJECT on error"
                    exit("REJECT")
                    # print "Error: " + currToken
                else:
                    tokenList.append(Token('NUM', currToken))
                    # print "NUM: " + currToken
                currToken = ""
                setFlag(c)
            elif flags["symbolFlag"]:  # if symbol flagged
                currToken += str(c)
                # print finished symbols
                if currToken in finSymbols or \
                        (currToken == "*" and
                         commentDepth == 0):  # if token is a finished symbol
                    tokenList.append(Token('symbol', currToken))
                    # print currToken  # print token
                    currToken = ""  # reset token
                    resetFlags()  # reset flags
                    continue
                # handle ambiguous symbols
                c = next(lineIter, None)  # get next c
                # handle "/"
                if currToken == "/":
                    if c == "*":  # if "/*"
                        commentDepth += 1
                        currToken = ""
                        resetFlags()
                    elif c == "/":  # if "//"
                        # skip rest of line
                        currToken = ""  # reset token
                        resetFlags()  # reset flags
                        break  # exit while loop
                    else:  # if "/?"
                        tokenList.append(Token('symbol', currToken))
                        # print currToken  # print token
                        currToken = ""  # reset token
                        setFlag(c)  # set flag with new c
                # handle "<", ">", "=", "!"
                elif currToken in ("<", ">", "=", "!"):
                    if c == "=":  # if "<=" (etc...)
                        tokenList.append(Token('symbol', currToken + c))
                        # print currToken + c  # print completed token
                        currToken = ""  # reset token
                        resetFlags()  # reset flags
                    elif currToken == "!":  # if token is "!?"
                        # print "REJECT on error"
                        exit("REJECT")
                        # print "Error: " + currToken  # output error
                        currToken = ""  # reset token
                        setFlag(c)  # reset flags
                    else:  # if "<?"
                        tokenList.append(Token('symbol', currToken))
                        # print currToken  # print "<"
                        currToken = ""  # reset token
                        setFlag(c)  # set flag with new c
            elif flags["whitespaceFlag"]:  # if ws flagged
                while re.match(r'\s', c):  # while in whitespace
                    c = next(lineIter, None)  # get next c
                setFlag(c)  # set flag with next non-whitespace char
            elif flags["errorFlag"]:
                # print "REJECT on error"
                exit("REJECT")
                # print "Error: " + c
                resetFlags();
            else:  # otherwise, no flag set
                c = next(lineIter, None)
                setFlag(c)
    f.close()

except IOError:
    exit('Cannot open argument file...\nExiting')

# print "\n"
# for token in tokenList:
#     print token.tokType + ": " + token.tokVal


class Parser:

    def __init__(self, tokList):
        self.tokenList = tokList
        self.tokenIter = iter(self.tokenList)
        self.currToken = next(self.tokenIter, Token('$', '$'))

    def A(self):
        print "Entering A: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # B
            self.B()
        else:
            print "REJECT in A"
            exit("REJECT")


    def B(self):
        print "Entering B: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # CB'
            self.C()
            self.B_()
        else:
            print "REJECT in B"
            exit("REJECT")


    def B_(self):
        print "Entering B: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # CB'
            self.C()
            self.B_()
        elif self.currToken.tokVal == '$':
            return  # empty
        else:
            print "REJECT in B_"
            exit("REJECT")


    def C(self):
        print "Entering C: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaC'
            self.F()
            if self.currToken.tokType == "ID":
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.C_()
            else:
                print "REJECT in C"
                exit("REJECT")
        else:
            print "REJECT in C"
            exit("REJECT")

    def C_(self):
        print "Entering C_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "["):
            self.D_()
        elif self.currToken.tokVal == "(":
            # (G)H
            # accept a (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.G()
            if self.currToken.tokVal == ")":
                # accept a )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.H()
            else:
                print "REJECT in C_"
                exit("REJECT")
        else:
            print "REJECT in C_"
            exit("REJECT")

    def D(self):
        print "Entering D: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaD'
            self.F()
            if self.currToken.tokType == "ID":
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.D_()
            else:
                print "REJECT in D"
                exit("REJECT")
        else:
            print "REJECT in D"
            exit("REJECT")

    def D_(self):
        print "Entering D_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == ";":
            # ;
            # accept a ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        elif self.currToken.tokVal == "[":
            # [b];
            # accept a [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokType == "NUM":
                # accept a NUM
                self.currToken = next(self.tokenIter, Token('$', '$'))
                if self.currToken.tokVal == "]":
                    # accept a ]
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    if self.currToken.tokVal == ";":
                        # accept a ;
                        self.currToken = next(self.tokenIter, Token('$', '$'))
                    else:
                        print "REJECT in D_"
                        exit("REJECT")
                else:
                    print "REJECT in D_"
                    exit("REJECT")
            else:
                print "REJECT in D_"
                exit("REJECT")
        else:
            print "REJECT in D_"
            exit("REJECT")

    def F(self):
        print "Entering F: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # accept token
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            print "REJECT in F"
            exit("REJECT")

    def E(self):
        print "Entering E: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # Fa(G)H
            self.F()
            if self.currToken.tokType == "ID":
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                if self.currToken.tokVal == "(":
                    # accept a (
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    self.G()
                    if self.currToken.tokVal == ")":
                        # accept a )
                        self.currToken = next(self.tokenIter, Token('$', '$'))
                        self.H()
                    else:
                        print "REJECT in E"
                        exit("REJECT")
                else:
                    print "REJECT in E"
                    exit("REJECT")
            else:
                print "REJECT in E"
                exit("REJECT")
        else:
            print "REJECT in E"
            exit("REJECT")

    def G(self):
        print "Entering G: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("int", "float"):
            # caJ'I'
            # accept int
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokType == "ID":
                # accept ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.J_()
                self.I_()
            else:
                print "REJECT in G"
                exit("REJECT")
        elif self.currToken.tokVal == "void":
            # dG'
            # accept a void
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.G_()
        else:
            print "REJECT in G"
            exit("REJECT")

    def G_(self):
        print "Entering G_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType == "ID":
            # aJ'I'
            # accept an ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.J_()
            self.I_()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            print "REJECT in G_"
            exit("REJECT")

    def I(self):
        print "Entering I: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # JI'
            self.J()
            self.I_()
        else:
            print "REJECT in I"
            exit("REJECT")

    def I_(self):
        print "Entering I_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == ",":
            # ,JI'
            # accept: ,
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.J()
            self.I_()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            print "REJECT in I_"
            exit("REJECT")

    def J(self):
        print "Entering J: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaJ'
            self.F()
            if self.currToken.tokType == "ID":
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.J_()
            else:
                print "REJECT in J"
                exit("REJECT")
        else:
            print "REJECT in J"
            exit("REJECT")

    def J_(self):
        print "Entering J_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "[":
            # []
            # accept: [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "]":
                # accept: ]
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in J_"
                exit("REJECT")
        elif self.currToken.tokVal in (")", ","):
            return  # empty
        else:
            print "REJECT in J_"
            exit("REJECT")

    def H(self):
        print "Entering H: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "{":
            # {KL}
            # accept: {
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.K()
            self.L()
            if self.currToken.tokVal == "}":
                # accept: }
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in H"
                exit("REJECT")
        else:
            print "REJECT in H"
            exit("REJECT")

    def K(self):
        print "Entering K: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "int", "float", "void", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # K'
            self.K_()
        else:
            print "REJECT in K"
            exit("REJECT")

    def K_(self):
        print "Entering K_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # DK'
            self.D()
            self.K_()
        elif self.currToken.tokVal in (";", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            return  # empty
        else:
            print "REJECT in K_"
            exit("REJECT")

    def L(self):
        print "Entering L: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # L'
            self.L_()
        else:
            print "REJECT in L"
            exit("REJECT")

    def L_(self):
        print "Entering L_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "(", ")", "{", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # ML'
            self.M()
            self.L_()
        elif self.currToken.tokVal == "}":
            return  # empty
        else:
            print "REJECT in L_"
            exit("REJECT")

    def M(self):
        print "Entering M: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "(") or self.currToken.tokType in ("ID", "NUM"):
            # N
            self.N()
        elif self.currToken.tokVal == "{":
            # H
            self.H()
        elif self.currToken.tokVal == "if":
            # O
            self.O()
        elif self.currToken.tokVal == "while":
            # P
            self.P()
        elif self.currToken.tokVal == "return":
            # Q
            self.Q()
        else:
            print "REJECT in M"
            exit("REJECT")

    def N(self):
        print "Entering N: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R;
            self.R()
            if self.currToken.tokVal == ";":
                # accept: ;
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in N"
                exit("REJECT")
        elif self.currToken.tokVal == ";":
            # ;
            # accept: ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            print "REJECT in N"
            exit("REJECT")

    def O(self):
        print "Entering O: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "if":
            # e(R)MO'
            # accept: if
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "(":
                # accept: (
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.R()
                if self.currToken.tokVal == ")":
                    # accept: )
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    self.M()
                    self.O_()
                else:
                    print "REJECT in O"
                    exit("REJECT")
            else:
                print "REJECT in O"
                exit("REJECT")
        else:
            print "REJECT in O"
            exit("REJECT")

    def O_(self):
        print "Entering O_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "else":
            # fM | @
            # accept: else
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.M()
        elif self.currToken.tokVal in (";", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            return  # empty
        else:
            print "REJECT in O_"
            exit("REJECT")

    def P(self):
        print "Entering P: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "while":
            # g(R)M
            # accept: while
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "(":
                # accept: (
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.R()
                if self.currToken.tokVal == ")":
                    # accept: )
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    self.M()
                else:
                    print "REJECT in P"
                    exit("REJECT")
            else:
                print "REJECT in P"
                exit("REJECT")
        else:
            print "REJECT in P"
            exit("REJECT")

    def Q(self):
        print "Entering Q: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "return":
            # hQ'
            # accept: return
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.Q_()
        else:
            print "REJECT in Q"
            exit("REJECT")

    def Q_(self):
        print "Entering Q_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R;
            self.R()
            if self.currToken.tokVal == ";":
                # accept: ;
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in Q_"
                exit("REJECT")
        elif self.currToken.tokVal == ";":
            # ;
            # accept: ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            print "REJECT in Q_"
            exit("REJECT")

    def R(self):
        print "Entering R: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType == "ID":
            # aR'
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R_()
        elif self.currToken.tokType == "NUM":
            # bX'V'T'
            # accept: NUM
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.X_()
            self.V_()
            self.T_()
        elif self.currToken.tokVal == "(":
            # (R)X'V'T'
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R()
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.X_()
                self.V_()
                self.T_()
            else:
                print "REJECT in R"
                exit("REJECT")
        else:
            print "REJECT in R"
            exit("REJECT")

    def R_(self):
        print "Entering R_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "[", "]", ")", "=", "<=",	"<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # S'R''
            self.S_()
            self.R__()
        elif self.currToken.tokVal == "(":
            # (2)X'V'T'
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self._2()
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.X_()
                self.V_()
                self.T_()
            else:
                print "REJECT in R_"
                exit("REJECT")
        else:
            print "REJECT in R_"
            exit("REJECT")

    def R__(self):
        print "Entering R__: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in (";", "]", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # X'V'T'
            self.X_()
            self.V_()
            self.T_()
        elif self.currToken.tokVal == "=":
            # =R
            # accept: =
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R()
        else:
            print "REJECT in R__"
            exit("REJECT")

    def S(self):
        print "Entering S: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType == "ID":
            # aS'
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.S_()
        else:
            print "REJECT in S"
            exit("REJECT")

    def S_(self):
        print "Entering S_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == "[":
            # [R]
            # accept: [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R()
            if self.currToken.tokVal == "]":
                # accept: ]
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in S_"
                exit("REJECT")
        elif self.currToken.tokVal in (";", ")", "]=", "=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            return  # empty
        else:
            print "REJECT in S_"
            exit("REJECT")

    def T(self):
        print "Entering T: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # VT'
            self.V()
            self.T_()
        else:
            print "REJECT in T"
            exit("REJECT")

    def T_(self):
        print "Entering T_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("<=", "<", ">", ">=", "==", "!="):
            # UV
            self.U()
            self.V()
        elif self.currToken.tokVal in (";", ")", "]", ","):
            return  # empty
        else:
            print "REJECT in T_"
            exit("REJECT")

    def U(self):
        print "Entering U: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("<=", "<", ">", ">=", "==", "!="):
            # relop
            # accept: relop
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            print "REJECT in U"
            exit("REJECT")

    def V(self):
        print "Entering V: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # XV'
            self.X()
            self.V_()
        else:
            print "REJECT in V"
            exit("REJECT")

    def V_(self):
        print "Entering V_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("+", "-"):
            # WXV'
            self.W()
            self.X()
            self.V_()
        elif self.currToken.tokVal in (";", ")", "<=", "<", ">", ">=", "==", "!=", "]", ","):
            return  # empty
        else:
            print "REJECT in V_"
            exit("REJECT")

    def W(self):
        print "Entering W: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("+", "-"):
            # addop
            # accept: addop
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            print "REJECT in W"
            exit("REJECT")

    def X(self):
        print "Entering X: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # ZX'
            self.Z()
            self.X_()
        else:
            print "REJECT in X"
            exit("REJECT")

    def X_(self):
        print "Entering X_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("*", "/"):
            # YZX'
            self.Y()
            self.Z()
            self.X_()
        elif self.currToken.tokVal in (";", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "]", ","):
            return  # empty
        else:
            print "REJECT in X_"
            exit("REJECT")

    def Y(self):
        print "Entering Y: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("*", "/"):
            # mulop
            # accept: mulop
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            print "REJECT in Y"
            exit("REJECT")

    def Z(self):
        print "Entering Z: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType == "ID":
            # aZ'
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.Z_()
        elif self.currToken.tokType == "NUM":
            # b
            # accept: NUM
            self.currToken = next(self.tokenIter, Token('$', '$'))
        elif self.currToken.tokVal == "(":
            # ( R )
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R()
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in Z"
                exit("REJECT")
        else:
            print "REJECT in Z"
            exit("REJECT")

    def Z_(self):
        print "Entering Z_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal in ("[", ";", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", "]"):
            # S'
            self.S_()
        elif self.currToken.tokVal == "(":
            # (2)
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self._2()
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                print "REJECT in Z_"
                exit("REJECT")
        else:
            print "REJECT in Z_"
            exit("REJECT")

    def _1(self):
        print "Entering _1: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType == "ID":
            # a(2)
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "(":
                # accept: (
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self._2()
                if self.currToken.tokVal == ")":
                    # accept: )
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                else:
                    print "REJECT in _1"
                    exit("REJECT")
            else:
                print "REJECT in _1"
                exit("REJECT")
        else:
            print "REJECT in _1"
            exit("REJECT")

    def _2(self):
        print "Entering _2: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # 3
            self._3()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            print "REJECT in _2"
            exit("REJECT")

    def _3(self):
        print "Entering _3: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R3'
            self.R()
            self._3_()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            print "REJECT in _3"
            exit("REJECT")

    def _3_(self):
        print "Entering _3_: " + self.currToken.tokType + ": " + self.currToken.tokVal
        if self.currToken.tokVal == ",":
            # ,R3'
            # accept: ,
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R()
            self._3_()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            print "REJECT in _3_"
            exit("REJECT")

    def parse(self):
        self.A()
        exit("ACCEPT")


# PARSE TOKENS
p = Parser(tokenList)
p.parse()






























