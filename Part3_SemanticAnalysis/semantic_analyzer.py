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
        self.isFloat = False


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
        # log(input line if not blank)
        # if len(line) > 0:
        #     log("INPUT(" + str(lineNum) + "): " + line  # display input line)
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
                    # log("keyword: " + currToken)
                    currToken = ""
                    setFlag(c)
                # otherwise, token is an ID
                else:
                    tokenList.append(Token('ID', currToken))
                    # log("ID: " + currToken)
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
                    # log("REJECT on error")
                    exit("REJECT")
                    # log("Error: " + currToken)
                else:
                    tokenList.append(Token('NUM', currToken))
                    tokenList[len(tokenList) - 1].isFloat = isFloat
                    # log(currToken + "=" + tokenList[len(tokenList) - 1].tokVal)
                    # log("NUM: " + currToken)
                currToken = ""
                setFlag(c)
            elif flags["symbolFlag"]:  # if symbol flagged
                currToken += str(c)
                # log(finished symbols)
                if currToken in finSymbols or \
                        (currToken == "*" and
                         commentDepth == 0):  # if token is a finished symbol
                    tokenList.append(Token('symbol', currToken))
                    # log(currToken)  # print token
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
                        # log(currToken)  # print token
                        currToken = ""  # reset token
                        setFlag(c)  # set flag with new c
                # handle "<", ">", "=", "!"
                elif currToken in ("<", ">", "=", "!"):
                    if c == "=":  # if "<=" (etc...)
                        tokenList.append(Token('symbol', currToken + c))
                        # log(currToken + c)  # print completed token
                        currToken = ""  # reset token
                        resetFlags()  # reset flags
                    elif currToken == "!":  # if token is "!?"
                        # log("REJECT on error")
                        exit("REJECT")
                        # log("Error: " + currToken)  # output error
                        currToken = ""  # reset token
                        setFlag(c)  # reset flags
                    else:  # if "<?"
                        tokenList.append(Token('symbol', currToken))
                        # log(currToken)  # print "<"
                        currToken = ""  # reset token
                        setFlag(c)  # set flag with new c
            elif flags["whitespaceFlag"]:  # if ws flagged
                while re.match(r'\s', c):  # while in whitespace
                    c = next(lineIter, None)  # get next c
                setFlag(c)  # set flag with next non-whitespace char
            elif flags["errorFlag"]:
                # log("REJECT on error")
                exit("REJECT")
                # log("Error: " + c)
                resetFlags()
            else:  # otherwise, no flag set
                c = next(lineIter, None)
                setFlag(c)
    f.close()

except IOError:
    exit('Cannot open argument file...\nExiting')

# print "\n"
# for token in tokenList:
#     print token.tokType + ": " + token.tokVal


def log(content):
    on = False
    if on:
        print(content)


class Symbol:

    def __init__(self, sType, sID):
        self.type = sType
        self.id = sID
        self.paramTypes = None
        self.length = None


class Scope:

    def __init__(self, pScope):
        self.symbolTable = {}  # symbol table is a dictionary
        self.next = None
        self.previous = pScope

    def isGlobalScope(self):
        if self.previous is None:
            return True
        else:
            return False


class SymbolTable:

    def __init__(self):
        self.globalScope = Scope(None)  # Global scope has no parent scope
        self.localScope = self.globalScope  # global scope is local scope initially

    def newScope(self):
        self.localScope.next = Scope(self.localScope)  # create new next scope
        self.localScope = self.localScope.next  # set local scope to next scope

    def endLocalScope(self):
        self.localScope = self.localScope.previous

    def addSymbolToLocalScope(self, sType, sID):
        if sID in self.localScope.symbolTable:
            exit("REJECT")
        else:
            self.localScope.symbolTable[sID] = Symbol(sType, sID)

    def testVariable(self, sID):
        if self.localScope.symbolTable[sID].type == "void":
            log("variable cannot be type void")
            exit("REJECT")

    def getSymbol(self, sID):
        currScope = self.localScope
        while currScope is not None:
            if sID in currScope.symbolTable:
                return currScope.symbolTable[sID]
            else:
                currScope = currScope.previous
        log("Symbol DNE: getSymbol()")
        exit("REJECT")  # symbol not found in any scope

    def getFuncSymbol(self, fID):
        if self.isFunction(fID):
            return self.getSymbol(fID)
        else:
            log("REJECT: symbol not declared as function from this scope")
            exit("REJECT")

    def getSymbolType(self, sid):
        currScope = self.localScope
        while currScope is not None:
            if sid in currScope.symbolTable:
                return currScope.symbolTable[sid].type
            else:
                currScope = currScope.previous
        log("Symbol DNE: getSymbolType()")
        exit("REJECT")  # symbol not found in any scope

    def getFunctionParams(self, sid):
        currScope = self.localScope
        while currScope is not None:
            if sid in currScope.symbolTable:
                if currScope.symbolTable[sid].paramTypes is None:
                    log("symbol not a function")
                    exit("REJECT")  # symbol not a function
                else:
                    return currScope.symbolTable[sid].paramTypes
            else:
                currScope = currScope.previous
        log("Symbol DNE: getFunctionParams()")
        exit("REJECT")  # symbol not found in any scope

    def getArrayLength(self, sid):
        currScope = self.localScope
        while currScope is not None:
            if sid in currScope.symbolTable:
                if currScope.symbolTable[sid].length is None:
                    log("symbol not an array")
                    exit("REJECT")  # symbol not an array
                else:
                    return currScope.symbolTable[sid].length
                # return currScope.symbolTable[sid].length  # None -> not an array
            else:
                currScope = currScope.previous
        log("Symbol DNE: getArrayLength()")
        exit("REJECT")  # symbol not found in any scope

    def setParamTypes(self, fID, typeArray):
        self.globalScope.symbolTable[fID].paramTypes = typeArray

    def setSymbolArrayLength(self, sID, aLength):
        self.localScope.symbolTable[sID].length = aLength

    def isArray(self, sID):
        if self.getSymbol(sID).length is not None:
            return True
        else:
            return False

    def isFunction(self, sID):
        s = self.getSymbol(sID)
        # if sID in self.globalScope.symbolTable:
        if s.paramTypes is not None:
            return True
        else:
            return False
        # else:
        #     return False


class Parser:

    def __init__(self, tokList):
        self.tokenList = tokList
        self.tokenIter = iter(self.tokenList)
        self.currToken = next(self.tokenIter, Token('$', '$'))
        self.symbolTable = SymbolTable()
        self.semanticFlags = {"main-declared": False, "func-stmt": False, "func-call": False, "func-returned": False}
        self.semanticDict = {"type-specifier": "", "ID": "", "func-ID": "", "func-type": "",
                             "param-types": [], "arg-count": 0}

    def testExpression(self, sList):
        """Takes a List of symbols to compare"""
        opList = []
        for symbol in sList:
            if symbol is not None:
                opList.append(symbol)
        if len(opList) == 0:  # if no symbols
            return None  # no symbols to return
        elif len(opList) == 1:  # if 1 symbol
            return opList[0]  # only 1 symbol to return
        else:  # otherwise, more than 1 symbol
            for i in range(len(opList) - 1):  # then compare symbol types
                if opList[i].type != opList[i+1].type:  # if types don't match
                    log("illegal expression: testExpression()")
                    exit("REJECT")  # illegal expression
            return opList[0]

    def A(self):  # Program
        log("Entering A: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # B
            self.B()
        else:
            log("REJECT in A")
            exit("REJECT")

    def B(self):  # Declaration-list
        log("Entering B: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # CB'
            self.C()
            self.B_()
        else:
            log("REJECT in B")
            exit("REJECT")

    def B_(self):  # Declaration-list'
        log("Entering B: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # CB'
            self.C()
            self.B_()
        elif self.currToken.tokVal == '$':
            if not self.semanticFlags["main-declared"]:
                log("REJECT in B_: no main declared")
            return  # empty
        else:
            log("REJECT in B_")
            exit("REJECT")

    def C(self):  # Declaration
        log("Entering C: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaC'
            self.F()
            if self.currToken.tokType == "ID":
                # semantic: capture ID
                self.semanticDict["ID"] = self.currToken.tokVal  # could be var or function
                # Add symbol to symbol table
                self.symbolTable.addSymbolToLocalScope(self.semanticDict["type-specifier"],
                                                       self.semanticDict["ID"])
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.C_()
            else:
                log("REJECT in C")
                exit("REJECT")
        else:
            log("REJECT in C")
            exit("REJECT")

    def C_(self):  # Declaration'
        log("Entering C_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "["):
            # D'
            # semantic: symbol was variable
            self.symbolTable.testVariable(self.semanticDict["ID"])  # test variable not void
            self.D_()
        elif self.currToken.tokVal == "(":
            # (G)H
            # TODO: reset return flag,
            # semantic: symbol was function
            self.semanticDict["func-ID"] = self.semanticDict["ID"]  # capture function ID
            self.semanticDict["func-type"] = self.symbolTable.getSymbol(self.semanticDict["func-ID"]).type
            if self.semanticFlags["main-declared"]:  # if declaring a function and main already declared
                log("REJECT in C_: main function must be last")
                exit("REJECT")
            elif self.semanticDict["func-ID"] == "main":  # handle main
                self.semanticFlags["main-declared"] = True  # raise flag
            self.symbolTable.newScope()  # new scope for function  parameters
            self.semanticFlags["func-stmt"] = True  # entering function statement
            # accept a (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.G()
            if self.currToken.tokVal == ")":
                # semantic: give param types to current function
                self.symbolTable.setParamTypes(self.semanticDict["func-ID"],
                                               self.semanticDict["param-types"][:])
                # accept a )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.H()
                # semantic: end of fun-declaration
                if not self.semanticFlags["func-returned"] and self.semanticDict["func-type"] in ("int", "float"):
                    log("REJECT in C_: " + self.semanticDict["func-type"] + " function did not return")
                    exit("REJECT")
                self.semanticFlags["func-returned"] = False  # reset return flag
                self.semanticFlags["func-stmt"] = False  # exiting function statement
            else:
                log("REJECT in C_")
                exit("REJECT")
        else:
            log("REJECT in C_")
            exit("REJECT")

    def D(self):  # Var-declaration
        log("Entering D: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaD'
            self.F()
            if self.currToken.tokType == "ID":
                # capture semantic: ID
                self.semanticDict["ID"] = self.currToken.tokVal
                # add var to symbol table
                self.symbolTable.addSymbolToLocalScope(self.semanticDict["type-specifier"],
                                                       self.semanticDict["ID"])
                # semantic: symbol was variable
                self.symbolTable.testVariable(self.semanticDict["ID"])  # test for void variable
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.D_()
            else:
                log("REJECT in D")
                exit("REJECT")
        else:
            log("REJECT in D")
            exit("REJECT")

    def D_(self):  # Var-declaration'
        log("Entering D_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == ";":
            # ;
            # accept a ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        elif self.currToken.tokVal == "[":
            # [b];
            # accept a [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokType == "NUM" and not self.currToken.isFloat:
                # semantic: capture array length
                self.symbolTable.setSymbolArrayLength(self.semanticDict["ID"],
                                                      self.currToken.tokVal)
                # accept a NUM
                self.currToken = next(self.tokenIter, Token('$', '$'))
                if self.currToken.tokVal == "]":
                    # accept a ]
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    if self.currToken.tokVal == ";":
                        # accept a ;
                        self.currToken = next(self.tokenIter, Token('$', '$'))
                    else:
                        log("REJECT in D_")
                        exit("REJECT")
                else:
                    log("REJECT in D_")
                    exit("REJECT")
            else:
                log("REJECT in D_")
                exit("REJECT")
        else:
            log("REJECT in D_")
            exit("REJECT")

    def F(self):  # Type-specifier
        log("Entering F: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # semantic: capture type-specifier
            self.semanticDict["type-specifier"] = self.currToken.tokVal
            # accept token
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in F")
            exit("REJECT")

    def E(self):  # Fun-declaration
        log("Entering E: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # Fa(G)H
            # TODO: reset return flag
            self.F()
            if self.currToken.tokType == "ID":
                # capture semantic: ID
                self.semanticDict["ID"] = self.currToken.tokVal
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                if self.currToken.tokVal == "(":
                    # semantic: symbol was function
                    self.semanticDict["func-ID"] = self.semanticDict["ID"]  # capture function ID
                    self.semanticDict["func-type"] = self.symbolTable.getSymbol(self.semanticDict["func-ID"]).type
                    if self.semanticFlags["main-declared"]:  # if declaring a function and main already declared
                        log("REJECT in C_: main function must be last")
                        exit("REJECT")
                    elif self.semanticDict["func-ID"] == "main":  # handle main
                        self.semanticFlags["main-declared"] = True  # raise flag
                    self.symbolTable.newScope()  # new function scope for parameters
                    self.semanticFlags["func-stmt"] = True  # entering function statement
                    # accept a (
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    self.G()
                    if self.currToken.tokVal == ")":
                        # semantic: give param types to current function
                        self.symbolTable.setParamTypes(self.semanticDict["func-ID"],
                                                       self.semanticDict["param-types"][:])
                        # accept a )
                        self.currToken = next(self.tokenIter, Token('$', '$'))
                        self.H()
                        # semantic: end of fun-declaration
                        if not self.semanticFlags["func-returned"] and \
                                self.semanticDict["func-type"] in ("int", "float"):
                            log("REJECT in C_: " + self.semanticDict["func-type"] + " function did not return")
                            exit("REJECT")
                        self.semanticFlags["func-returned"] = False  # reset return flag
                        self.semanticFlags["func-stmt"] = False  # exiting function statement
                    else:
                        log("REJECT in E")
                        exit("REJECT")
                else:
                    log("REJECT in E")
                    exit("REJECT")
            else:
                log("REJECT in E")
                exit("REJECT")
        else:
            log("REJECT in E")
            exit("REJECT")

    def G(self):  # params
        log("Entering G: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        # reset semantic params
        self.semanticDict["param-types"] = []
        if self.currToken.tokVal in ("int", "float"):
            # caJ'I'
            # semantic: capture type-specifier
            self.semanticDict["type-specifier"] = self.currToken.tokVal
            self.semanticDict["param-types"].append(self.currToken.tokVal)  # add type to type list
            # accept int/float
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokType == "ID":
                # semantic: capture ID
                self.semanticDict["ID"] = self.currToken.tokVal
                # add symbol to table
                self.symbolTable.addSymbolToLocalScope(self.semanticDict["type-specifier"],
                                                       self.semanticDict["ID"])
                # accept ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.J_()
                self.I_()
            else:
                log("REJECT in G")
                exit("REJECT")
        elif self.currToken.tokVal == "void":
            # dG'
            # semantic: capture type-specifier
            self.semanticDict["type-specifier"] = self.currToken.tokVal
            self.semanticDict["param-types"].append(self.currToken.tokVal)  # add type to type list
            # accept a void
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.G_()
        else:
            log("REJECT in G")
            exit("REJECT")

    def G_(self):  # params'
        log("Entering G_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # aJ'I'
            # semantic: capture ID
            self.semanticDict["ID"] = self.currToken.tokVal
            # add symbol to table
            self.symbolTable.addSymbolToLocalScope(self.semanticDict["type-specifier"],
                                                   self.semanticDict["ID"])
            # accept an ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.J_()
            self.I_()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            log("REJECT in G_")
            exit("REJECT")

    def I(self):  # Param-list
        log("Entering I: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # JI'
            self.J()
            self.I_()
        else:
            log("REJECT in I")
            exit("REJECT")

    def I_(self):  # Param-list'
        log("Entering I_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == ",":
            # ,JI'
            # accept: ,
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.J()
            self.I_()
        elif self.currToken.tokVal == ")":
            return  # empty
        else:
            log("REJECT in I_")
            exit("REJECT")

    def J(self):  # param
        log("Entering J: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaJ'
            self.F()
            # semantic: add type-specifier to param type list
            self.semanticDict["param-types"].append(self.semanticDict["type-specifier"])
            if self.currToken.tokType == "ID":
                # capture semantic: ID
                self.semanticDict["ID"] = self.currToken.tokVal
                # add var to symbol table
                self.symbolTable.addSymbolToLocalScope(self.semanticDict["type-specifier"],
                                                       self.semanticDict["ID"])
                # accept an ID
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.J_()
            else:
                log("REJECT in J")
                exit("REJECT")
        else:
            log("REJECT in J")
            exit("REJECT")

    def J_(self):  # param'
        log("Entering J_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "[":
            # []
            # semantic: symbol was variable
            self.symbolTable.testVariable(self.semanticDict["ID"])  # test for void variable
            # semantic: variable is an array
            self.symbolTable.setSymbolArrayLength(self.semanticDict["ID"], -1)  # length unknown
            self.semanticDict["param-types"][len(self.semanticDict["param-types"]) - 1] += "[]"  # param is array
            # accept: [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "]":
                # accept: ]
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in J_")
                exit("REJECT")
        elif self.currToken.tokVal in (")", ","):
            # semantic: symbol was variable
            self.symbolTable.testVariable(self.semanticDict["ID"])  # test for void variable
            return  # empty
        else:
            log("REJECT in J_")
            exit("REJECT")

    def H(self):  # Compound-stmt
        log("Entering H: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "{":
            # {KL}
            # semantic: new scope if not beginning of a function
            if self.semanticFlags["func-stmt"]:
                self.semanticFlags["func-stmt"] = False
            else:
                self.symbolTable.newScope()
            # accept: {
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.K()
            self.L()
            if self.currToken.tokVal == "}":
                # semantic: end local scope
                self.symbolTable.endLocalScope()
                # accept: }
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in H")
                exit("REJECT")
        else:
            log("REJECT in H")
            exit("REJECT")

    def K(self):  # Local-declarations
        log("Entering K: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "int", "float", "void", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # K'
            self.K_()
        else:
            log("REJECT in K")
            exit("REJECT")

    def K_(self):  # Local-declarations'
        log("Entering K_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # DK'
            self.D()
            self.K_()
        elif self.currToken.tokVal in (";", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            return  # empty
        else:
            log("REJECT in K_")
            exit("REJECT")

    def L(self):  # Statement-list
        log("Entering L: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # L'
            self.L_()
        else:
            log("REJECT in L")
            exit("REJECT")

    def L_(self):  # Statement-list'
        log("Entering L_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "(", ")", "{", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # ML'
            self.M()
            self.L_()
        elif self.currToken.tokVal == "}":
            return  # empty
        else:
            log("REJECT in L_")
            exit("REJECT")

    def M(self):  # statement
        log("Entering M: " + self.currToken.tokType + ": " + self.currToken.tokVal)
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
            log("REJECT in M")
            exit("REJECT")

    def N(self):  # Expression-stmt
        log("Entering N: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R;
            self.R()
            if self.currToken.tokVal == ";":
                # accept: ;
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in N")
                exit("REJECT")
        elif self.currToken.tokVal == ";":
            # ;
            # accept: ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in N")
            exit("REJECT")

    def O(self):  # Selection-stmt
        log("Entering O: " + self.currToken.tokType + ": " + self.currToken.tokVal)
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
                    log("REJECT in O")
                    exit("REJECT")
            else:
                log("REJECT in O")
                exit("REJECT")
        else:
            log("REJECT in O")
            exit("REJECT")

    def O_(self):  # Selection-stmt'
        log("Entering O_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "else":
            # fM | @
            # accept: else
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.M()
        elif self.currToken.tokVal in (";", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            return  # empty
        else:
            log("REJECT in O_")
            exit("REJECT")

    def P(self):  # Iteration-stmt
        log("Entering P: " + self.currToken.tokType + ": " + self.currToken.tokVal)
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
                    log("REJECT in P")
                    exit("REJECT")
            else:
                log("REJECT in P")
                exit("REJECT")
        else:
            log("REJECT in P")
            exit("REJECT")

    def Q(self):  # Return-stmt
        log("Entering Q: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "return":
            # hQ'
            # semantic: function has return
            self.semanticFlags["func-returned"] = True
            # accept: return
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.Q_()
        else:
            log("REJECT in Q")
            exit("REJECT")

    def Q_(self):  # Return-stmt'
        log("Entering Q_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R;
            # TODO: expression must match func-type, func-type must not be void
            expr = self.R()
            if self.semanticDict["func-type"] != expr.type:
                log("REJECT in Q_: return type conflict: " + expr.type + " is not " + self.semanticDict["func-type"])
                exit("REJECT")
            elif self.semanticDict["func-type"] == "void":
                log("REJECT in Q_: void returning expression")
                exit("REJECT")
            # elif expr.length is not None:
            #     log("REJECT in Q_: cannot return array")
            #     exit("REJECT")
            if self.currToken.tokVal == ";":
                # accept: ;
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in Q_")
                exit("REJECT")
        elif self.currToken.tokVal == ";":
            # ;
            # semantic: func-type must be void for empty return
            if self.semanticDict["func-type"] != "void":
                log("REJECT in Q_: empty return for " + self.semanticDict["func-type"] + " function")
                exit("REJECT")
            # accept: ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in Q_")
            exit("REJECT")

    def R(self):  # expression
        log("Entering R: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # aR'
            # semantic: check table for id
            symb = self.symbolTable.getSymbol(self.currToken.tokVal)
            self.semanticDict["ID"] = self.currToken.tokVal  # capture ID
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            expr = self.R_()
            return self.testExpression([symb, expr])
        elif self.currToken.tokType == "NUM":
            # bX'V'T'
            if self.currToken.isFloat:
                type = "float"
            else:
                type = "int"
            num = Symbol(type,"NUM")
            # accept: NUM
            self.currToken = next(self.tokenIter, Token('$', '$'))
            term = self.X_()
            adde = self.V_()
            sime = self.T_()
            return self.testExpression([num, term, adde, sime])
        elif self.currToken.tokVal == "(":
            # (R)X'V'T'
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            expr = self.R()
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                term = self.X_()
                adde = self.V_()
                sime = self.T_()
                return self.testExpression([expr, term, adde, sime])
            else:
                log("REJECT in R")
                exit("REJECT")
        else:
            log("REJECT in R")
            exit("REJECT")

    def R_(self):  # expression'
        log("Entering R_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "[", "]", ")", "=", "<=",	"<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # S'R''
            self.S_()
            return self.R__()
        elif self.currToken.tokVal == "(":
            # (2)X'V'T'
            # semantic: verify symbol is function
            if not self.symbolTable.isFunction(self.semanticDict["ID"]):
                log("REJECT in R_: " + self.semanticDict["ID"] + " not a declared function from this scope")
                exit("REJECT")
            funcSymbol = self.symbolTable.getFuncSymbol(self.semanticDict["ID"])
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            args = self._2()
            if args is None:
                args = [Symbol("void", None)]
            if self.currToken.tokVal == ")":
                # semantic: check function arguments
                if args[0].type == "void" and funcSymbol.paramTypes[0] != "void":
                    log("REJECT in R_: no arguments passed to " + \
                          str(len(funcSymbol.paramTypes)) + " argument function: " + funcSymbol.id)
                    exit("REJECT")
                elif len(funcSymbol.paramTypes) != len(args):
                    log("REJECT in R_: arg count != to param count")
                    exit("REJECT")
                elif len(funcSymbol.paramTypes) == len(args):
                    for i in range(len(args)):
                        if funcSymbol.paramTypes[i] != args[i].type:
                            log("REJECT in R_: param mismatch")
                            exit("REJECT")
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                term = self.X_()
                adde = self.V_()
                sime = self.T_()
                return self.testExpression([term, adde, sime])
            else:
                log("REJECT in R_")
                exit("REJECT")
        else:
            log("REJECT in R_")
            exit("REJECT")

    def R__(self):  # expression''
        log("Entering R__: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "]", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # X'V'T'
            term = self.X_()
            adde = self.V_()
            sime = self.T_()
            return self.testExpression([term, adde, sime])
        elif self.currToken.tokVal == "=":
            # =R
            # accept: =
            self.currToken = next(self.tokenIter, Token('$', '$'))
            return self.R()
        else:
            log("REJECT in R__")
            exit("REJECT")

    def S(self):  # var
        log("Entering S: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # aS'
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.S_()
        else:
            log("REJECT in S")
            exit("REJECT")

    def S_(self):  # var'
        log("Entering S_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "[":
            # [R]
            # semantic: verify ID was declared as array
            self.symbolTable.getArrayLength(self.semanticDict["ID"])
            # accept: [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.R()
            if self.currToken.tokVal == "]":
                # accept: ]
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in S_")
                exit("REJECT")
        elif self.currToken.tokVal in (";", ")", "]", "=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # TODO: allow if array being passed as paramater
            if self.symbolTable.isArray(self.semanticDict["ID"]):
                log("REJECT in S_: " + self.semanticDict["ID"] + " declared as array")
                exit("REJECT")
            elif self. symbolTable.isFunction(self.semanticDict["ID"]):
                log("REJECT in S_: " + self.semanticDict["ID"] + " declared as function")
                exit("REJECT")
            return None  # empty
        else:
            log("REJECT in S_")
            exit("REJECT")

    def T(self):  # Simple-expression
        log("Entering T: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # VT'
            ls = self.V()
            rs = self.T_()
            if rs is not None:  # if T' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    exit("REJECT")
            else:  # otherwise, no symbol from T'
                return ls
        else:
            log("REJECT in T")
            exit("REJECT")

    def T_(self):  # Simple-expression'
        log("Entering T_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("<=", "<", ">", ">=", "==", "!="):
            # UV
            self.U()
            return self.V()
        elif self.currToken.tokVal in (";", ")", "]", ","):
            return None  # empty
        else:
            log("REJECT in T_")
            exit("REJECT")

    def U(self):  # relop
        log("Entering U: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("<=", "<", ">", ">=", "==", "!="):
            # relop
            # accept: relop
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in U")
            exit("REJECT")

    def V(self):  # Additive-expression
        log("Entering V: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # XV'
            ls = self.X()
            rs = self.V_()
            if rs is not None:  # if V' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    log("Reject in V: types do not match")
                    exit("REJECT")
            else:  # otherwise, no symbol from V'
                return ls
        else:
            log("REJECT in V")
            exit("REJECT")

    def V_(self):  # Additive-expression'
        log("Entering V_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("+", "-"):
            # WXV'
            self.W()
            ls = self.X()
            rs = self.V_()
            if rs is not None:  # if V' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    log("Reject in V_: types do not match")
                    exit("REJECT")
            else:  # otherwise, no symbol from V'
                return ls
        elif self.currToken.tokVal in (";", ")", "<=", "<", ">", ">=", "==", "!=", "]", ","):
            return None  # empty
        else:
            log("REJECT in V_")
            exit("REJECT")

    def W(self):  # addop
        log("Entering W: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("+", "-"):
            # addop
            # accept: addop
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in W")
            exit("REJECT")

    def X(self):  # term
        log("Entering X: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # ZX'
            ls = self.Z()
            rs = self.X_()
            if rs is not None:  # if X' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    log("Reject in X: types do not match")
                    exit("REJECT")
            else:  # otherwise, no symbol from X'
                return ls
        else:
            log("REJECT in X")
            exit("REJECT")

    def X_(self):  # term'
        log("Entering X_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("*", "/"):
            # YZX'
            self.Y()
            ls = self.Z()
            rs = self.X_()
            if rs is not None:  # if X' returns a symbol
                if ls.type == rs.type:  # if ls is the same type as rs
                    return ls
                else:  # otherwise, no match
                    log("Reject in X_: types do not match")
                    exit("REJECT")
            else:  # otherwise, no symbol from X'
                return ls
        elif self.currToken.tokVal in (";", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "]", ","):
            return None  # empty
        else:
            log("REJECT in X_")
            exit("REJECT")

    def Y(self):  # mulop
        log("Entering Y: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("*", "/"):
            # mulop
            # accept: mulop
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in Y")
            exit("REJECT")

    def Z(self):  # factor
        log("Entering Z: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # aZ'
            # semantic: check symbol
            self.semanticDict["ID"] = self.currToken.tokVal
            factor = self.symbolTable.getSymbol(self.semanticDict["ID"])
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.Z_()
            return factor
        elif self.currToken.tokType == "NUM":
            # b
            # semantic: get NUM type
            if self.currToken.isFloat:
                type = "float"
            else:
                type = "int"
            factor = Symbol(type,"NUM")
            # accept: NUM
            self.currToken = next(self.tokenIter, Token('$', '$'))
            return factor
        elif self.currToken.tokVal == "(":
            # ( R )
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            factor = self.R()
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                return factor
            else:
                log("REJECT in Z")
                exit("REJECT")
        else:
            log("REJECT in Z")
            exit("REJECT")

    def Z_(self):  # factor'
        log("Entering Z_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("[", ";", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", "]"):
            # S'
            self.S_()
        elif self.currToken.tokVal == "(":
            # (2)
            # semantic: verify symbol is function
            if not self.symbolTable.isFunction(self.semanticDict["ID"]):
                log("REJECT in R_: " + self.semanticDict["ID"] + " not a declared function")
                exit("REJECT")
            funcSymbol = self.symbolTable.getFuncSymbol(self.semanticDict["ID"])
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            args = self._2()
            if args is None:
                args = [Symbol("void", None)]
            if self.currToken.tokVal == ")":
                # semantic: check function arguments
                if args[0].type == "void" and funcSymbol.paramTypes[0] != "void":
                    log("REJECT in Z_: no arguments passed to " + \
                          str(len(funcSymbol.paramTypes)) + " argument function: " + funcSymbol.id)
                    exit("REJECT")
                elif len(funcSymbol.paramTypes) != len(args):
                    log("REJECT in Z_: arg count != to param count")
                    exit("REJECT")
                elif len(funcSymbol.paramTypes) == len(args):
                    for i in range(len(args)):
                        if funcSymbol.paramTypes[i] != args[i].type:
                            # TODO: handle array params
                            log("REJECT in Z_: param mismatch")
                            exit("REJECT")
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in Z_")
                exit("REJECT")
        else:
            log("REJECT in Z_")
            exit("REJECT")

    def _1(self):  # call
        log("Entering _1: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # a(2)
            # semantic: capture & check symbol
            self.semanticDict["ID"] = self.currToken.tokVal
            factor = self.symbolTable.getSymbol(self.semanticDict["ID"])
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "(":
                # semantic: symbol was function
                # self.semanticDict["func-ID"] = self.semanticDict["ID"]
                func = self.symbolTable.getSymbol(self.semanticDict["ID"])
                # accept: (
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self._2()
                if self.currToken.tokVal == ")":
                    # accept: )
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    return func
                else:
                    log("REJECT in _1")
                    exit("REJECT")
            else:
                log("REJECT in _1")
                exit("REJECT")
        else:
            log("REJECT in _1")
            exit("REJECT")

    def _2(self):  # args
        log("Entering _2: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # 3
            return self._3()
        elif self.currToken.tokVal == ")":
            return None  # empty
        else:
            log("REJECT in _2")
            exit("REJECT")

    def _3(self):  # Arg-list
        log("Entering _3: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R3'
            arg = self.R()
            args = self._3_()
            if args is None:
                return [arg]
            else:
                arglist = [arg]
                arglist.extend(args)
                return arglist
        else:
            log("REJECT in _3")
            exit("REJECT")

    def _3_(self):  # Arg-list'
        log("Entering _3_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == ",":
            # ,R3'
            # accept: ,
            self.currToken = next(self.tokenIter, Token('$', '$'))
            arg = self.R()
            args = self._3_()
            if args is None:
                return [arg]
            else:
                arglist = [arg]
                arglist.extend(args)
                return arglist
        elif self.currToken.tokVal == ")":
            return None  # empty
        else:
            log("REJECT in _3_")
            exit("REJECT")

    def parse(self):
        self.A()
        exit("ACCEPT")


# PARSE TOKENS
p = Parser(tokenList)
p.parse()






























