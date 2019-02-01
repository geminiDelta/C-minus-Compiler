# lexical_analyzer.py
# Written by: Austin Green
# Description: Lexical analyzer for Compilers course

import re
from sys import argv, exit


# FUNCTIONS
def resetFlags():
    """Reset all flags to False"""
    for flag in flags:
        flags[flag] = False


def setFlag(tokenChar):
    """Set a flag based on input"""
    resetFlags()    # set all flags to False
    if tokenChar is None:
        return None
    if re.match(r'[a-z]', tokenChar):      # if letter
        flags["letterFlag"] = True      # set letter flag
    elif re.match(r'\d', tokenChar):    # if number
        flags["numberFlag"] = True      # set number flag
    elif tokenChar in allSymbols or \
            tokenChar == "!":           # if symbol
        flags["symbolFlag"] = True      # set symbol flag
    elif re.match(r'\s', tokenChar):    # if whitespace
        flags["whitespaceFlag"] = True  # set ws flag
    else:                           # otherwise, invalid character
        flags["errorFlag"] = True   # set error flag


def flagSet():
    """Return true if a flag is set; False otherwise"""
    for flag in flags:
        if flags[flag]:
            return True
    return False


# VARIABLES
# Analyzer variables
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
        if len(line) > 0:
            print "INPUT(" + str(lineNum) + "): " + line  # display input line
        # scan line (iterator)
        lineIter = iter(line)  # initialize iterator for line
        c = ""
        while c is not None:  # while line has more characters
            if commentDepth > 0:                # if in block comment
                c = next(lineIter, None)
                if c != "/" and c != "*":    # if c not comment character
                    currToken = ""          # clear token
                    continue                # move on
                # look for /*
                elif currToken + c == "/*":
                    commentDepth += 1   # increment comment depth
                    currToken = ""      # reset token
                # look for */
                elif currToken + c == "*/":
                    commentDepth -= 1   # decrement comment depth
                    currToken = ""      # reset token
                else:   # "/" or "*"
                    currToken = c
            elif flags["letterFlag"]:             # if letter flagged
                while c is not None and re.match(r'[a-z]', c):
                    currToken += c
                    c = next(lineIter, None)
                # check if token is keyword
                if currToken in keywords:
                    print "keyword: " + currToken
                    currToken = ""
                    setFlag(c)
                # otherwise, token is an ID
                else:
                    print "ID: " + currToken
                    currToken = ""
                    setFlag(c)
            elif flags["numberFlag"]:           # if number flagged
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
                    print "Error: " + currToken
                else:
                    print "NUM: " + currToken
                currToken = ""
                setFlag(c)
            elif flags["symbolFlag"]:           # if symbol flagged
                currToken += str(c)
                # print finished symbols
                if currToken in finSymbols or \
                        (currToken == "*" and
                         commentDepth == 0):    # if token is a finished symbol
                    print currToken     # print token
                    currToken = ""      # reset token
                    resetFlags()        # reset flags
                    continue
                # handle ambiguous symbols
                c = next(lineIter, None)    # get next c
                # handle "/"
                if currToken == "/":
                    if c == "*":            # if "/*"
                        commentDepth += 1
                        currToken = ""
                        resetFlags()
                    elif c == "/":      # if "//"
                        # skip rest of line
                        currToken = ""  # reset token
                        resetFlags()    # reset flags
                        break           # exit while loop
                    else:               # if "/?"
                        print currToken  # print token
                        currToken = ""  # reset token
                        setFlag(c)      # set flag with new c
                # handle "<", ">", "=", "!"
                elif currToken in ("<", ">", "=", "!"):
                    if c == "=":            # if "<=" (etc...)
                        print currToken + c  # print completed token
                        currToken = ""      # reset token
                        resetFlags()        # reset flags
                    elif currToken == "!":  # if token is "!?"
                        print "Error: " + currToken  # output error
                        currToken = ""      # reset token
                        setFlag(c)          # reset flags
                    else:                   # if "<?"
                        print currToken     # print "<"
                        currToken = ""      # reset token
                        setFlag(c)          # set flag with new c
            elif flags["whitespaceFlag"]:       # if ws flagged
                while re.match(r'\s', c):   # while in whitespace
                    c = next(lineIter, None)      # get next c
                setFlag(c)                  # set flag with next non-whitespace char
            elif flags["errorFlag"]:
                print "Error: " + c
                resetFlags();
            else:                               # otherwise, no flag set
                c = next(lineIter, None)
                setFlag(c)

except IOError:
    exit('Cannot open argument file...\nExiting')
