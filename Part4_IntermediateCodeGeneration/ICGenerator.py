# ICGenerator.py
# Written by: Austin Green
# Description: Intermediate Code Generator for Compilers course

import re
from sys import argv, exit


# LA CLASSES
class Token:
    def __init__(self, tokType, tokVal):
        self.tokType = tokType  # symbol, keyword, ID, NUM
        self.tokVal = tokVal
        self.isFloat = False

# GENERAL FUNCTIONS
def reject():
    active = False
    if active:
        exit("REJECT")


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
                    reject()
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
                        reject()
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
                reject()
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


def getOp(operator):
    # "<", "<=", ">=", ">", "==", "!="
    if operator == "<":
        return "lt"
    elif operator == "<=":
        return "le"
    elif operator == ">=":
        return "ge"
    elif operator == ">":
        return "gt"
    elif operator == "<=":
        return "eq"
    elif operator == "<=":
        return "ne"
    return ""


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
            reject()
        else:
            self.localScope.symbolTable[sID] = Symbol(sType, sID)

    def testVariable(self, sID):
        if self.localScope.symbolTable[sID].type == "void":
            log("variable cannot be type void")
            reject()

    def getSymbol(self, sID):
        currScope = self.localScope
        while currScope is not None:
            if sID in currScope.symbolTable:
                return currScope.symbolTable[sID]
            else:
                currScope = currScope.previous
        log("Symbol DNE: getSymbol()")
        reject()  # symbol not found in any scope

    def getFuncSymbol(self, fID):
        if self.isFunction(fID):
            return self.getSymbol(fID)
        else:
            log("REJECT: symbol not declared as function from this scope")
            reject()

    def getSymbolType(self, sid):
        currScope = self.localScope
        while currScope is not None:
            if sid in currScope.symbolTable:
                return currScope.symbolTable[sid].type
            else:
                currScope = currScope.previous
        log("Symbol DNE: getSymbolType()")
        reject()  # symbol not found in any scope

    def getFunctionParams(self, sid):
        currScope = self.localScope
        while currScope is not None:
            if sid in currScope.symbolTable:
                if currScope.symbolTable[sid].paramTypes is None:
                    log("symbol not a function")
                    reject()  # symbol not a function
                else:
                    return currScope.symbolTable[sid].paramTypes
            else:
                currScope = currScope.previous
        log("Symbol DNE: getFunctionParams()")
        reject()  # symbol not found in any scope

    def getArrayLength(self, sid):
        currScope = self.localScope
        while currScope is not None:
            if sid in currScope.symbolTable:
                if currScope.symbolTable[sid].length is None:
                    log("symbol not an array")
                    reject()  # symbol not an array
                else:
                    return currScope.symbolTable[sid].length
                # return currScope.symbolTable[sid].length  # None -> not an array
            else:
                currScope = currScope.previous
        log("Symbol DNE: getArrayLength()")
        reject()  # symbol not found in any scope

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


class TreeNode:

    def __init__(self, token):
        self.token = token
        self.lChild = None
        self.rChild = None
        self.parent = None


class Tree:

    def __init__(self):
        self.root = None
        self.nodeList = []

    def addNextOp(self, opTok):
        """if the current root is an operand, set the root as the new op and the operand as the left child"""
        opNode = TreeNode(opTok)
        self.nodeList.append(opNode)
        if self.root.token.tokType in ("NUM", "ID"):  # if root is operand
            # temp = self.root
            opNode.lChild = self.root
            self.root = opNode
            opNode.lChild.parent = opNode
        else:  # otherwise, root is an OP
            if opNode.token.tokVal in ("*", "/"): # if new op is mulop
                # go to the right-most non-leaf
                currNode = self.root
                while currNode.rChild.token.tokType not in ("NUM", "ID"):
                    currNode = currNode.rChild
                if currNode.token.tokVal in ("*", "/"):  # if right-most non-leaf is mulop
                    # shift right-most op left and replace
                    opNode.parent = currNode.parent
                    opNode.lChild = currNode
                    currNode.parent = opNode
                    if opNode.parent is not None:
                        opNode.parent.rChild = opNode
                    else:
                        self.root = opNode
                else:  # otherwise, addop or relop
                    # insert new op as right-most op
                    opNode.parent = currNode
                    opNode.lChild = currNode.rChild
                    currNode.rChild = opNode
                    opNode.lChild.parent = opNode
            elif opNode.token.tokVal in ("*", "/"):  # if new op is addop
                currNode = self.root
                while currNode.rChild.token.tokType not in ("NUM", "ID") and \
                        currNode.token.tokVal not in ("+", "-"):  # get right-most op or addop
                    currNode = currNode.rChild
                if currNode.token.tokVal in ("+", "-"):  # if addop found
                    # shift right-most addop left and replace
                    opNode.parent = currNode.parent
                    opNode.lChild = currNode
                    currNode.parent = opNode
                    if opNode.parent is not None:
                        opNode.parent.rChild = opNode
                    else:
                        self.root = opNode
                else:  # otherwise, relop found
                    # insert new op as right-most op
                    opNode.parent = currNode
                    opNode.lChild = currNode.rChild
                    currNode.rChild = opNode
                    opNode.lChild.parent = opNode
            else:  # new op is relop
                # shift root left and replace
                currNode = self.root
                opNode.parent = currNode.parent  # should be None anyways
                opNode.lChild = currNode
                currNode.parent = opNode
                if opNode.parent is not None:  # should always be None
                    opNode.parent.rChild = opNode
                else:
                    self.root = opNode

    def addNextOperand(self, operandTok):
        operandNode = TreeNode(operandTok)
        self.nodeList.append(operandNode)
        currNode = self.root
        if currNode is None:
            self.root = operandNode
            return
        while currNode.rChild is not None:
            currNode = currNode.rChild
        currNode.rChild = operandNode

    def display_nodes(self, root):
        if root is None:
            return

        if root.lChild is not None:
            self.display_nodes(root.lChild)

        print(root.token.tokVal + " ")

        if root.rChild is not None:
            self.display_nodes(root.rChild)

    def display_nodelist(self):
        print "# of nodes: " + str(len(self.nodeList))
        for i in range(0, len(self.nodeList)):
            print str(self.nodeList[i].token.tokVal) + " ",
        print ""


class Tuple:

    def __init__(self):
        self.op = ''
        self.operand1 = ''
        self.operand2 = ''
        self.result = ''


class Parser:

    def __init__(self, tokList):
        self.tokenList = tokList
        self.tokenIter = iter(self.tokenList)
        self.currToken = next(self.tokenIter, Token('$', '$'))
        self.symbolTable = SymbolTable()
        self.semanticFlags = {"main-declared": False, "func-stmt": False, "func-call": False, "func-returned": False}
        self.semanticDict = {"type-specifier": "", "ID": "", "func-ID": "", "func-type": "",
                             "param-types": [], "arg-count": 0}
        self.tuples = []
        self.curTmpCount = 0  # ICG: track temp placeholders

    def tuplify(self, root):
        if root is None:
            return
        if root.lChild is None:
            return root.token.tokVal
        # log("Recursing to node: " + str(root.token.tokVal))
        lc = rc = None

        if root.lChild.token.tokType not in ("ID", "NUM"):
            lc = self.tuplify(root.lChild)

        # op reached
        t = Tuple()
        # set op
        if root.token.tokVal == '*':
            t.op = 'mult'
        elif root.token.tokVal == '/':
            t.op = 'div'
        elif root.token.tokVal == '+':
            t.op = 'add'
        elif root.token.tokVal == '-':
            t.op = 'sub'
        else:
            t.op = 'cmpr'
        # set opnd1
        if lc is None:
            t.operand1 = root.lChild.token.tokVal
        else:
            t.operand1 = lc  # should be _t#

        if root.rChild.token.tokType not in ("ID", "NUM"):
            rc = self.tuplify(root.rChild)

        # set opnd2
        if rc is None:
            t.operand2 = root.rChild.token.tokVal
        else:
            t.operand2 = rc  # should be _t#

        # set result
        t.result = self.get_newtemp()

        # add new tuple to tuples
        self.tuples.append(t)

        return t.result

    def get_newtemp(self):
            newTemp = '_t' + str(self.curTmpCount)  # produce new temp
            self.curTmpCount += 1  # increment temp count
            return newTemp

    def get_lasttemp(self):
        return '_t' + str(self.curTmpCount-1)

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
                    reject()  # illegal expression
            return opList[0]

    def A(self):  # Program
        log("Entering A: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # B
            self.B()
        else:
            log("REJECT in A")
            reject()

    def B(self):  # Declaration-list
        log("Entering B: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # CB'
            self.C()
            self.B_()
        else:
            log("REJECT in B")
            reject()

    def B_(self):  # Declaration-list'
        log("Entering B: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # CB'
            self.C()
            self.B_()
        elif self.currToken.tokVal == '$':
            # ICG: add end tuple
            self.tuples.append(Tuple())
            self.tuples[len(self.tuples)-1].op = "END"
            if not self.semanticFlags["main-declared"]:
                log("REJECT in B_: no main declared")
            return  # empty
        else:
            log("REJECT in B_")
            reject()

    def C(self):  # Declaration
        log("Entering C: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        # ICG: new tuple
        self.tuples.append(Tuple())
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
                reject()
        else:
            log("REJECT in C")
            reject()

    def C_(self):  # Declaration'
        log("Entering C_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "["):
            # D'
            self.tuples[len(self.tuples) - 1].op = 'alloc'  # ICG: allocating for variable
            self.tuples[len(self.tuples) - 1].result = self.semanticDict["ID"]  # ICG: variable was last ID
            # semantic: symbol was variable
            self.symbolTable.testVariable(self.semanticDict["ID"])  # test variable not void
            self.D_()
        elif self.currToken.tokVal == "(":
            # (G)H
            self.tuples[len(self.tuples) - 1].op = 'func'  # ICG: declaring function
            self.tuples[len(self.tuples) - 1].operand1 = self.semanticDict["ID"]  # ICG: func was last ID
            self.tuples[len(self.tuples) - 1].operand2 = self.semanticDict["type-specifier"]  # ICG: func has last type
            tIndex = len(self.tuples) - 1
            # semantic: symbol was function
            self.semanticDict["func-ID"] = self.semanticDict["ID"]  # capture function ID
            self.semanticDict["func-type"] = self.symbolTable.getSymbol(self.semanticDict["func-ID"]).type
            if self.semanticFlags["main-declared"]:  # if declaring a function and main already declared
                log("REJECT in C_: main function must be last")
                reject()
            elif self.semanticDict["func-ID"] == "main":  # handle main
                self.semanticFlags["main-declared"] = True  # raise flag
            self.symbolTable.newScope()  # new scope for function  parameters
            self.semanticFlags["func-stmt"] = True  # entering function statement
            # accept a (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.G()
            if self.currToken.tokVal == ")":
                # ICG
                if self.semanticDict["param-types"][0] != 'void':
                    self.tuples[tIndex].result = len(self.semanticDict["param-types"])  # ICG: func has params
                else:
                    self.tuples[len(self.tuples) - 1].result = 0  # ICG: func has no params
                # semantic: give param types to current function
                self.symbolTable.setParamTypes(self.semanticDict["func-ID"],
                                               self.semanticDict["param-types"][:])
                # accept a )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                self.H()
                # semantic: end of fun-declaration
                if not self.semanticFlags["func-returned"] and self.semanticDict["func-type"] in ("int", "float"):
                    log("REJECT in C_: " + self.semanticDict["func-type"] + " function did not return")
                    reject()
                self.semanticFlags["func-returned"] = False  # reset return flag
                self.semanticFlags["func-stmt"] = False  # exiting function statement
            else:
                log("REJECT in C_")
                reject()
        else:
            log("REJECT in C_")
            reject()

    def D(self):  # Var-declaration
        log("Entering D: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaD'
            # ICG: new tuple for var declaration
            self.tuples.append(Tuple())
            self.tuples[len(self.tuples)-1].op = 'alloc'
            self.F()
            if self.currToken.tokType == "ID":
                # ICG:
                self.tuples[len(self.tuples) - 1].result = self.currToken.tokVal
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
                reject()
        else:
            log("REJECT in D")
            reject()

    def D_(self):  # Var-declaration'
        log("Entering D_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == ";":
            # ;
            self.tuples[len(self.tuples)-1].operand1 = 4  # ICG: alloc 4 to simple variable
            # accept a ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        elif self.currToken.tokVal == "[":
            # [b];
            # accept a [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokType == "NUM" and not self.currToken.isFloat:
                # ICG: array alloc for tuple
                self.tuples[len(self.tuples)-1].operand1 = 4 * int(self.currToken.tokVal)
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
                        reject()
                else:
                    log("REJECT in D_")
                    reject()
            else:
                log("REJECT in D_")
                reject()
        else:
            log("REJECT in D_")
            reject()

    def F(self):  # Type-specifier
        log("Entering F: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # semantic: capture type-specifier
            self.semanticDict["type-specifier"] = self.currToken.tokVal
            # accept token
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in F")
            reject()

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
                        reject()
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
                            reject()
                        self.semanticFlags["func-returned"] = False  # reset return flag
                        self.semanticFlags["func-stmt"] = False  # exiting function statement
                    else:
                        log("REJECT in E")
                        reject()
                else:
                    log("REJECT in E")
                    reject()
            else:
                log("REJECT in E")
                reject()
        else:
            log("REJECT in E")
            reject()

    def G(self):  # params
        log("Entering G: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        # reset semantic params
        self.semanticDict["param-types"] = []
        if self.currToken.tokVal in ("int", "float"):
            # caJ'I'
            # ICG: tuple for param
            self.tuples.append(Tuple())
            self.tuples[len(self.tuples)-1].op = 'param'
            # semantic: capture type-specifier
            self.semanticDict["type-specifier"] = self.currToken.tokVal
            self.semanticDict["param-types"].append(self.currToken.tokVal)  # add type to type list
            # accept int/float
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokType == "ID":
                # ICG: tuple result = ID
                self.tuples[len(self.tuples)-1].result = self.currToken.tokVal
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
                reject()
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
            reject()

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
            reject()

    def I(self):  # Param-list
        log("Entering I: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # JI'
            self.J()
            self.I_()
        else:
            log("REJECT in I")
            reject()

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
            reject()

    def J(self):  # param
        log("Entering J: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ('int', 'float', 'void'):
            # FaJ'
            # ICG: new param
            self.tuples.append(Tuple())  # ICG: new tuple
            self.tuples[len(self.tuples) - 1].op = 'param'  # ICG: tuple for param
            self.F()
            # semantic: add type-specifier to param type list
            self.semanticDict["param-types"].append(self.semanticDict["type-specifier"])
            if self.currToken.tokType == "ID":
                # ICG: get ID for param tuple
                self.tuples[len(self.tuples) - 1].result = self.currToken.tokVal
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
                reject()
        else:
            log("REJECT in J")
            reject()

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
                reject()
        elif self.currToken.tokVal in (")", ","):
            # ICG: param not array -> alloc 4
            self.tuples.append(Tuple())  # ICG: new tuple for alloc
            self.tuples[len(self.tuples)-1].op = 'alloc'  # alloc
            self.tuples[len(self.tuples) - 1].operand1 = 4
            self.tuples[len(self.tuples) - 1].result = self.semanticDict["ID"]
            # semantic: symbol was variable
            self.symbolTable.testVariable(self.semanticDict["ID"])  # test for void variable
            return  # empty
        else:
            log("REJECT in J_")
            reject()

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
                reject()
        else:
            log("REJECT in H")
            reject()

    def K(self):  # Local-declarations
        log("Entering K: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "int", "float", "void", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # K'
            self.K_()
        else:
            log("REJECT in K")
            reject()

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
            reject()

    def L(self):  # Statement-list
        log("Entering L: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            # L'
            self.L_()
        else:
            log("REJECT in L")
            reject()

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
            reject()

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
            reject()

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
                reject()
        elif self.currToken.tokVal == ";":
            # ;
            # accept: ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in N")
            reject()

    def O(self):  # Selection-stmt
        log("Entering O: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "if":
            # e(R)MO'
            # ICG: TODO
            # accept: if
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "(":
                # accept: (
                self.currToken = next(self.tokenIter, Token('$', '$'))
                expr = self.R()
                cmprResult = expr[1][0]
                relop = expr[1][1].token.tokVal
                if self.currToken.tokVal == ")":
                    # accept: )
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    # ICG: after if relop expression
                    self.tuples.append(Tuple())
                    self.tuples[len(self.tuples) - 1].op = "BR" + str(getOp(relop)).upper()
                    self.tuples[len(self.tuples) - 1].result = len(self.tuples) + 1
                    self.tuples.append(Tuple())
                    self.tuples[len(self.tuples) - 1].op = "BR"
                    bpif = len(self.tuples) - 1
                    self.M()
                    self.tuples[bpif].result = len(self.tuples)
                    self.O_()
                else:
                    log("REJECT in O")
                    reject()
            else:
                log("REJECT in O")
                reject()
        else:
            log("REJECT in O")
            reject()

    def O_(self):  # Selection-stmt'
        log("Entering O_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "else":
            # fM | @
            self.tuples.append(Tuple())
            self.tuples[len(self.tuples)-1].op = "BR"
            bpelse = len(self.tuples)-1
            # accept: else
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.M()
            self.tuples[bpelse].result = len(self.tuples)
        elif self.currToken.tokVal in (";", "(", "{", "}", "if", "while", "return") \
                or self.currToken.tokType in ("ID", "NUM"):
            return  # empty
        else:
            log("REJECT in O_")
            reject()

    def P(self):  # Iteration-stmt
        log("Entering P: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "while":
            # g(R)M
            # ICG: top of while TODO: while
            bpTopOfWhile = len(self.tuples)  # ICG: next tuple marks beginning of while loop
            # accept: while
            self.currToken = next(self.tokenIter, Token('$', '$'))
            if self.currToken.tokVal == "(":
                # accept: (
                self.currToken = next(self.tokenIter, Token('$', '$'))
                expr = self.R()
                lastResult = expr[1][0]
                relop = expr[1][1]
                if self.currToken.tokVal == ")":
                    # accept: )
                    self.currToken = next(self.tokenIter, Token('$', '$'))
                    # ICG: after if relop expression
                    self.tuples.append(Tuple())
                    self.tuples[len(self.tuples) - 1].op = "BR" + str(getOp(relop)).upper()
                    self.tuples[len(self.tuples) - 1].result = len(self.tuples) + 1
                    self.tuples.append(Tuple())
                    self.tuples[len(self.tuples) - 1].op = "BR"
                    bpwhile = len(self.tuples) - 1
                    self.M()
                    self.tuples.append(Tuple())
                    self.tuples[len(self.tuples) - 1].op = "BR"
                    self.tuples[len(self.tuples) - 1].result = bpTopOfWhile
                    self.tuples[bpwhile].result = len(self.tuples)
                else:
                    log("REJECT in P")
                    reject()
            else:
                log("REJECT in P")
                reject()
        else:
            log("REJECT in P")
            reject()

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
            reject()

    def Q_(self):  # Return-stmt'
        log("Entering Q_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R;
            # ICG: return
            self.tuples.append(Tuple())
            self.tuples[len(self.tuples)-1].op = 'return'
            expr = self.R()
            lastResult = expr[1][0]
            lastOp = expr[1][1]
            expr = expr[0]
            self.tuples[len(self.tuples) - 1].result = lastResult
            if self.semanticDict["func-type"] != expr.type:
                log("REJECT in Q_: return type conflict: " + expr.type + " is not " + self.semanticDict["func-type"])
                reject()
            elif self.semanticDict["func-type"] == "void":
                log("REJECT in Q_: void returning expression")
                reject()
            # elif expr.length is not None:
            #     log("REJECT in Q_: cannot return array")
            #     reject()
            if self.currToken.tokVal == ";":
                # ICG: return nothing
                self.tuples.append(Tuple())
                self.tuples[len(self.tuples) - 1].op = 'return'
                # accept: ;
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in Q_")
                reject()
        elif self.currToken.tokVal == ";":
            # ;
            # semantic: func-type must be void for empty return
            if self.semanticDict["func-type"] != "void":
                log("REJECT in Q_: empty return for " + self.semanticDict["func-type"] + " function")
                reject()
            # accept: ;
            self.currToken = next(self.tokenIter, Token('$', '$'))
        else:
            log("REJECT in Q_")
            reject()

    def R(self):  # expression
        log("Entering R: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        # ICG: init expression tree
        eTree = Tree()
        if self.currToken.tokType == "ID":
            # aR'
            # ICG: ID becomes root of tree
            eTree.addNextOperand(self.currToken)
            # semantic: check table for id
            symb = self.symbolTable.getSymbol(self.currToken.tokVal)
            self.semanticDict["ID"] = self.currToken.tokVal  # capture ID
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            expr = self.R_(eTree)
            # eTree.display_nodes(eTree.root)
            # eTree.display_nodelist()
            lastResult = self.tuplify(eTree.root)
            return self.testExpression([symb, expr]), (lastResult, eTree.root)
        elif self.currToken.tokType == "NUM":
            # bX'V'T'
            # ICG: NUM becomes root of tree
            eTree.root = TreeNode(self.currToken)
            if self.currToken.isFloat:
                type = "float"
            else:
                type = "int"
            num = Symbol(type, "NUM")
            # accept: NUM
            self.currToken = next(self.tokenIter, Token('$', '$'))
            term = self.X_(eTree)  # mulop factor X' | @
            adde = self.V_(eTree)  # addop term V' | @
            sime = self.T_(eTree)  # relop add-exp | @
            lastResult = self.tuplify(eTree.root)
            return self.testExpression([num, term, adde, sime]), (lastResult, eTree.root)
        elif self.currToken.tokVal == "(":
            # (R)X'V'T'
            # ICG: TODO
            # accept: (
            self.currToken = next(self.tokenIter, Token('$', '$'))
            expr = self.R()
            lastResult = expr[1][0]
            lastRoot = expr[1][1]
            expr = expr[0]
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                term = self.X_(eTree)  # mulop factor X' | @
                adde = self.V_(eTree)  # addop term V' | @
                sime = self.T_(eTree)  # relop add-exp | @
                lastResult = self.tuplify(eTree.root)
                return self.testExpression([expr, term, adde, sime]), (lastResult, eTree.root)
            else:
                log("REJECT in R")
                reject()
        else:
            log("REJECT in R")
            reject()

    def R_(self, eTree):  # expression'
        log("Entering R_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "[", "]", ")", "=", "<=",	"<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # S'R''
            self.S_()
            return self.R__(eTree)
        elif self.currToken.tokVal == "(":
            # (2)X'V'T'
            # semantic: verify symbol is function
            if not self.symbolTable.isFunction(self.semanticDict["ID"]):
                log("REJECT in R_: " + self.semanticDict["ID"] + " not a declared function from this scope")
                reject()
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
                    reject()
                elif len(funcSymbol.paramTypes) != len(args):
                    log("REJECT in R_: arg count != to param count")
                    reject()
                elif len(funcSymbol.paramTypes) == len(args):
                    for i in range(len(args)):
                        if funcSymbol.paramTypes[i] != args[i].type:
                            log("REJECT in R_: param mismatch")
                            reject()
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                term = self.X_(eTree)  # mulop factor X' | @
                adde = self.V_(eTree)  # addop term V' | @
                sime = self.T_(eTree)  # relop add-exp | @
                return self.testExpression([term, adde, sime])
            else:
                log("REJECT in R_")
                reject()
        else:
            log("REJECT in R_")
            reject()

    def R__(self, eTree):  # expression''
        log("Entering R__: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in (";", "]", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # X'V'T'
            term = self.X_(eTree)  # mulop factor X' | @
            adde = self.V_(eTree)  # addop term V' | @
            sime = self.T_(eTree)  # relop add-exp | @
            return self.testExpression([term, adde, sime])
        elif self.currToken.tokVal == "=":
            # =R
            assignee = self.semanticDict["ID"]
            # accept: =
            self.currToken = next(self.tokenIter, Token('$', '$'))
            expr = self.R()
            lastResult = expr[1][0]
            # lastOp = expr[1][1].token.tokVal
            expr = expr[0]
            # ICG: assign R to last ID
            self.tuples.append(Tuple())
            self.tuples[len(self.tuples)-1].op = "assign"
            self.tuples[len(self.tuples) - 1].operand1 = lastResult
            self.tuples[len(self.tuples) - 1].result = assignee
            return expr
        else:
            log("REJECT in R__")
            reject()

    def S(self):  # var
        log("Entering S: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # aS'
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.S_()
        else:
            log("REJECT in S")
            reject()

    def S_(self):  # var'
        log("Entering S_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == "[":
            # [R]
            # semantic: verify ID was declared as array
            self.symbolTable.getArrayLength(self.semanticDict["ID"])
            # accept: [
            self.currToken = next(self.tokenIter, Token('$', '$'))
            expr = self.R()
            subExpr = expr[1]
            expr = expr[0]
            if self.currToken.tokVal == "]":
                # accept: ]
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in S_")
                reject()
        elif self.currToken.tokVal in (";", ")", "]", "=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/", ","):
            # TODO: semantic: allow if array being passed as paramater
            if self.symbolTable.isArray(self.semanticDict["ID"]):
                log("REJECT in S_: " + self.semanticDict["ID"] + " declared as array")
                reject()
            elif self. symbolTable.isFunction(self.semanticDict["ID"]):
                log("REJECT in S_: " + self.semanticDict["ID"] + " declared as function")
                reject()
            return None  # empty
        else:
            log("REJECT in S_")
            reject()

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
                    reject()
            else:  # otherwise, no symbol from T'
                return ls
        else:
            log("REJECT in T")
            reject()

    def T_(self, eTree):  # Simple-expression'
        log("Entering T_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("<=", "<", ">", ">=", "==", "!="):
            # UV
            relop = self.U()
            # ICG: add relop to tree
            eTree.addNextOp(relop)
            return self.V(eTree)
        elif self.currToken.tokVal in (";", ")", "]", ","):
            return None  # empty
        else:
            log("REJECT in T_")
            reject()

    def U(self):  # relop
        log("Entering U: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("<=", "<", ">", ">=", "==", "!="):
            # relop
            # ICG: capture relop
            relop = self.currToken
            # accept: relop
            self.currToken = next(self.tokenIter, Token('$', '$'))
            return relop  # ICG: give relop to caller
        else:
            log("REJECT in U")
            reject()

    def V(self, eTree):  # Additive-expression
        log("Entering V: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # XV'
            ls = self.X(eTree)
            rs = self.V_(eTree)
            if rs is not None:  # if V' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    log("Reject in V: types do not match")
                    reject()
            else:  # otherwise, no symbol from V'
                return ls
        else:
            log("REJECT in V")
            reject()

    def V_(self, eTree):  # Additive-expression'
        log("Entering V_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("+", "-"):
            # WXV'
            addop = self.W()
            # ICG: add addop to tree
            eTree.addNextOp(addop)
            ls = self.X(eTree)
            rs = self.V_(eTree)
            if rs is not None:  # if V' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    log("Reject in V_: types do not match")
                    reject()
            else:  # otherwise, no symbol from V'
                return ls
        elif self.currToken.tokVal in (";", ")", "<=", "<", ">", ">=", "==", "!=", "]", ","):
            return None  # empty
        else:
            log("REJECT in V_")
            reject()

    def W(self):  # addop
        log("Entering W: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("+", "-"):
            # addop
            addop = self.currToken
            # accept: addop
            self.currToken = next(self.tokenIter, Token('$', '$'))
            return addop
        else:
            log("REJECT in W")
            reject()

    def X(self, eTree):  # term
        log("Entering X: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # ZX'
            ls = self.Z(eTree)
            rs = self.X_(eTree)
            if rs is not None:  # if X' returns a symbol
                if ls.type == rs.type:  # and if ls is the same type as rs
                    return ls  # return symbol
                else:  # otherwise, no match
                    log("Reject in X: types do not match")
                    reject()
            else:  # otherwise, no symbol from X'
                return ls
        else:
            log("REJECT in X")
            reject()

    def X_(self, eTree):  # term'
        log("Entering X_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("*", "/"):
            # YZX'
            mulop = self.Y()
            # ICG: add mulop to tree
            eTree.addNextOp(mulop)
            ls = self.Z(eTree)
            rs = self.X_(eTree)
            # ICG: tuple for mult op TODO
            # self.tuples.append(Tuple())  # ICG: new tuple
            # self.tuples[len(self.tuples)-1].op = 'mult'  # for multiplication
            # self.tuples[len(self.tuples) - 1].operand2 = ls.id  # ICG: opnd 2 is id from Z()
            # self.tuples[len(self.tuples) - 1].result = self.get_newtemp()  # ICG:
            if rs is not None:  # if X' returns a symbol
                # ICG: more expression to come

                if ls.type == rs.type:  # if ls is the same type as rs
                    return ls
                else:  # otherwise, no match
                    log("Reject in X_: types do not match")
                    reject()
            else:  # otherwise, no symbol from X'
                # ICG: no more expression to come
                return ls
        elif self.currToken.tokVal in (";", ")", "<=", "<", ">", ">=", "==", "!=", "+", "-", "]", ","):
            return None  # empty
        else:
            log("REJECT in X_")
            reject()

    def Y(self):  # mulop
        log("Entering Y: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal in ("*", "/"):
            # mulop
            # ICG: capture mulop
            mulop = self.currToken
            # accept: mulop
            self.currToken = next(self.tokenIter, Token('$', '$'))
            return mulop
        else:
            log("REJECT in Y")
            reject()

    def Z(self, eTree):  # factor
        log("Entering Z: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType == "ID":
            # aZ'
            # ICG: ID is next operand
            eTree.addNextOperand(self.currToken)
            # semantic: check symbol
            self.semanticDict["ID"] = self.currToken.tokVal
            factor = self.symbolTable.getSymbol(self.semanticDict["ID"])
            # accept: ID
            self.currToken = next(self.tokenIter, Token('$', '$'))
            self.Z_()
            return factor
        elif self.currToken.tokType == "NUM":
            # b
            # ICG: NUM is next operand
            eTree.addNextOperand(self.currToken)
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
            subExpr = factor[1]
            factor = factor[0]
            if self.currToken.tokVal == ")":
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
                return factor
            else:
                log("REJECT in Z")
                reject()
        else:
            log("REJECT in Z")
            reject()

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
                reject()
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
                    reject()
                elif len(funcSymbol.paramTypes) != len(args):
                    log("REJECT in Z_: arg count != to param count")
                    reject()
                elif len(funcSymbol.paramTypes) == len(args):
                    for i in range(len(args)):
                        if funcSymbol.paramTypes[i] != args[i].type:
                            # TODO: semantic: handle array params
                            log("REJECT in Z_: param mismatch")
                            reject()
                # accept: )
                self.currToken = next(self.tokenIter, Token('$', '$'))
            else:
                log("REJECT in Z_")
                reject()
        else:
            log("REJECT in Z_")
            reject()

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
                    reject()
            else:
                log("REJECT in _1")
                reject()
        else:
            log("REJECT in _1")
            reject()

    def _2(self):  # args
        log("Entering _2: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # 3
            return self._3()
        elif self.currToken.tokVal == ")":
            return None  # empty
        else:
            log("REJECT in _2")
            reject()

    def _3(self):  # Arg-list
        log("Entering _3: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokType in ("ID", "NUM") or self.currToken.tokVal == "(":
            # R3'
            arg = self.R()
            subExpr = arg[1]
            arg = arg[0]
            args = self._3_()
            if args is None:
                return [arg]
            else:
                arglist = [arg]
                arglist.extend(args)
                return arglist
        else:
            log("REJECT in _3")
            reject()

    def _3_(self):  # Arg-list'
        log("Entering _3_: " + self.currToken.tokType + ": " + self.currToken.tokVal)
        if self.currToken.tokVal == ",":
            # ,R3'
            # accept: ,
            self.currToken = next(self.tokenIter, Token('$', '$'))
            arg = self.R()
            subExpr = arg[1]
            arg = arg[0]
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
            reject()

    def parse(self):
        self.A()
        # exit("ACCEPT")
        # for i in range(5):
        #     self.tuples.append(Tuple())
        index = 0
        for t in self.tuples:
            # print "{:<5}{:<10}{:<10}{:<10}{:<10}".format(index, t.op, t.operand1, t.operand2, t.result)
            self.printTuple(index, t)
            index += 1

    def printTuple(self, index, t):
        print "{0:<5}{1:<10}{2:<10}{3:<10}{4:<10}".format(index, t.op, t.operand1, t.operand2, t.result)


# RUN PROGRAM
p = Parser(tokenList)
p.parse()






























