from constants import *
from NFA import *
from DFA import *
from models import *
from LEXER import *
from DFA_DIRECT import *
from utils import Grapher
import uuid

def testNFA():
    # r = ("a(a?b*|c+)b|baa")
    file_name = str(uuid.uuid4().fields[-1])[:5]
    r = ('(x|t)+((a|m)?)+')
    postfixExp = Convert_Infix_Postfix(r)
    postfixExp.replaceOperators() 
    postfixExp.toPostfix()
    print("Format expression: ", postfixExp.regex)
    print("Postfix expression: ", postfixExp.postfix)
    ########## NFA ##########
    nfaBuilt = build_thompson(postfixExp.postfix)
    nfaBuilt.showNFA(file_name)
    Grapher.drawNFA(nfaBuilt,file_name)
    
#testNFA()

# testNFA()
# drawMinDFASubsets
def testDFASubsets():
    file_name = str(uuid.uuid4().fields[-1])[:5]
    r = ("(A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)((A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)|(0|1|2|3|4|5|6|7|8|9))*")
    postfixExp = Convert_Infix_Postfix(r)
    postfixExp.replaceOperators() 
    postfixExp.toPostfix()
    thompson = build_thompson(postfixExp.postfix)
    dfa = DFASubsets(thompson)
    newAFD = dfa.create_DFASubset()
    print("postfix: ", postfixExp.postfix)
    #newAFD.showDFASubset(file_name)
    #Grapher.drawSubsetDFA(newAFD,file_name)
    Utils.simulate_exp(newAFD)

testDFASubsets()

# subsets minimzed
def testHoffman():
    file_name = str(uuid.uuid4().fields[-1])[:5]
    file_name = file_name+'_min'
    #r = ("(a|b)*a(a|b)(a|b)")
    r = ("0? (1? )? 0 ∗")
    print('min')
    postfixExp = Convert_Infix_Postfix(r)
    postfixExp.replaceOperators() 
    postfixExp.toPostfix()
    nfa = build_thompson(postfixExp.postfix)
    dfa_subsets = DFASubsets(nfa)
    dfa_subsets.create_DFASubset()
    dfa_subsets.min_DFASubset()
    dfa_subsets.showMinimized(file_name)
    Grapher.drawSubsetDFA(dfa_subsets,file_name)

#testHoffman()

def testTree():
    file_name = str(uuid.uuid4().fields[-1])[:5]
    r = ("(a|b)*(b|a)*abb")
    postfixExp = Convert_Infix_Postfix(r)
    augmented_exp = postfixExp.augmentRegex()
    
    direct = DFAfromTree(augmented_exp)
    newAFD = direct.buildDFADirect()
    newAFD.showDFADirect(file_name)
    
    Grapher.drawDirectDFA(newAFD,file_name)


#testTree()

# yalex
def testYalex():
    file_name = str(uuid.uuid4().fields[-1])[:5]
    yalexFile = "slr-4.yal"
    yalex = Lexer(yalexFile)
    individualRules = yalex.getIndividualRules()
    print("individualRules: ", individualRules)
    print()
    finalExp = yalex.getFinalExp()
    operators = yalex.getOperators()
    print("expression----")
    print(repr(finalExp))
    print()
    print("operators in use: ")
    print(operators)
    print()
    postfixExp = Convert_Infix_Postfix(finalExp)
    postfixExp.toPostfix()
    print("postfixExp----")
    print(repr(postfixExp.postfix))
    print()

    tree = Tree(postfixExp.postfix)
    tree.generateTree(tree.tree)
    tree.create_tree_table(file_name)

#testYalex()