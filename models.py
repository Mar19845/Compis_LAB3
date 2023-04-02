from typing import List, Dict

class AUTOMATON:
    def __init__(self, q:List[str], expression:str, alphabet:List[str], q0:str, f:str, transitions:List[str]):
        self.q = q
        self.expression = expression
        self.alphabet = alphabet
        self.q0 = q0
        self.f=f
        self.transitions = transitions
        
class TRANSITION:
    def __init__(self, start:str, transition:str, end:str):
        self.start = start
        self.transition = transition
        self.end = end
    
    def set_start(self, start):
        self.start = start
    
    def set_end(self, end):
        self.end = end
        
class STATE:
    def __init__(self, q0:str, f:str):
        self.q0 = q0
        self.f = f
        
class Tree(object):
    # symbol = string
    # left
    def __init__(self):
        self.left = None
        self.right = None
        self.symbol = None