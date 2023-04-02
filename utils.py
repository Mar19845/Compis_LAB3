import re
from graphviz import Digraph
import collections
from models import *
from constants import *
import os.path


class Utils():
    '''
    --------------- DIRECT  ---------------
    '''
    @staticmethod
    def check(dfa, new_state):
        for state in dfa:
            if collections.Counter(state.q0) == collections.Counter(new_state):
                return False
        return True
    
    @staticmethod
    def select(states, id):
        for state in states:
            if collections.Counter(state.q0) == collections.Counter(id):
                return state
        return False
    
    @staticmethod
    def important_states(tree):
        nodes = []
        if tree.symbol not in OPERATORS and tree.symbol != "ε" and tree.left == None and tree.right == None:
            nodes.append(tree)
        if tree.left != None:
            resp = Utils.important_states(tree.left)
            for i in resp:
                nodes.append(i)
        if tree.right != None:
            resp = Utils.important_states(tree.right)
            for i in resp:
                nodes.append(i)
        return nodes
    
    @staticmethod
    def nullable(tree):
        if tree.symbol == "ε":
            return True
        elif tree.symbol == ".":
            if Utils.nullable(tree.left) and Utils.nullable(tree.right):
                return True
        elif tree.symbol == "*":
            return True
        elif tree.symbol == "|":
            if Utils.nullable(tree.left) or Utils.nullable(tree.right):
                return True
            else:
                return False
        return False
    
    @staticmethod
    def first_position(tree):
        pos = []
        if tree.symbol in OPERATORS:
            if tree.symbol == "|":
                temp1 = Utils.first_position(tree.left)
                temp2 = Utils.first_position(tree.right)
                for num in temp1:
                    pos.append(num)
                for num in temp2:
                    pos.append(num)
            elif tree.symbol == "*":
                temp1 = Utils.first_position(tree.left)
                for num in temp1:
                    pos.append(num)
            elif tree.symbol == ".":
                temp1 = Utils.first_position(tree.left)
                for num in temp1:
                    pos.append(num)
                if Utils.nullable(tree.left):
                    temp2 = Utils.first_position(tree.right)
                    for num in temp2:
                        pos.append(num)
        
        elif tree.symbol != "ε":
            pos.append(tree)
        return pos
    
    @staticmethod
    def last_position(tree):
        pos = []
        if tree.symbol in OPERATORS:
            if tree.symbol == "|":
                temp1 = Utils.last_position(tree.left)
                temp2 = Utils.last_position(tree.right)
                for num in temp1:
                    pos.append(num)
                for num in temp2:
                    pos.append(num)
            elif tree.symbol == "*":
                temp1 = Utils.last_position(tree.left)
                for num in temp1:
                    pos.append(num)
            elif tree.symbol == ".":
                temp1 = Utils.last_position(tree.right)
                if Utils.nullable(tree.right):
                    temp2 = Utils.last_position(tree.left)
                    for num in temp2:
                        pos.append(num)
                for num in temp1:
                    pos.append(num)
            
        elif tree.symbol != "ε":
            pos.append(tree)
        return pos
    
    @staticmethod
    def followposition(tree, table):
        if tree.symbol == ".":
            temp1 = Utils.last_position(tree.left)
            temp2 = Utils.first_position(tree.right)
            for i in temp1:
                for num in temp2:
                    table[i].append(num)
        elif tree.symbol == "*":
            temp1 = Utils.last_position(tree)
            temp2 = Utils.first_position(tree)
            for i in temp1:
                for num in temp2:
                    table[i].append(num)
        elif tree.symbol == "+":
            temp1 = Utils.last_position(tree.left)
            temp2 = Utils.first_position(tree.left)
            for i in temp1:
                for num in temp2:
                    table[i].append(num)

        if tree.left != None:
            Utils.followposition(tree.left, table)
        if tree.right != None:
            Utils.followposition(tree.right, table)
    
    @staticmethod
    def directo(tree, exp):
        new_tree = Tree()
        new_tree.symbol = "."
        right_t = Tree()
        right_t.symbol = "#"
        new_tree.right = right_t
        new_tree.left = tree

        states_eval = Utils.important_states(new_tree)
        first = Utils.first_position(new_tree)
        last = Utils.last_position(new_tree)
        table = {}
        for pos in states_eval:
            table[pos] = []

        Utils.followposition(new_tree, table)
        inicial = Utils.first_position(new_tree)
        final = Utils.last_position(new_tree)
        #for tree in inicial: print(str(tree.symbol) + ',') 
        

        #for tree in final:print(str(tree.symbol) + "," )
        for key in table:
            x = "["
            key_string = str(key.symbol)
            for tree in table[key]:
                y = (str(tree.symbol) + ",")
                x += y
            x += "]"

        auto_direct = Utils.create(inicial, final, table, exp)

        return auto_direct
    
    @staticmethod
    def create(inicial, final, table, exp):
        first = STATE(inicial, 0)
        dfa_transitions = []
        dfa_states = [] 
        dfa_states.append(first)
        acceptance_states = []
        if final[-1] in first.q0:
            acceptance_states.append(first.f)

        symbols = []
        for symbol in exp:
            if symbol not in OPERATORS and symbol not in symbols and symbol != "ε":
                symbols.append(symbol)
        
        for state in dfa_states:
            for symbol in symbols:
                temp = []
                for pos in state.q0:
                    if pos.symbol == symbol:
                        tos = table[pos]
                        for t in tos:
                            if t not in temp:
                                temp.append(t)
                if Utils.check(dfa_states, temp) and temp != []:
                    new_state = STATE(temp, len(dfa_states))
                    if final[-1] in temp:
                        
                        acceptance_states.append(new_state.f)
                    
                    dfa_states.append(new_state)
                    transition1 = TRANSITION(start=state.f,transition=symbol,end=dfa_states[-1].f)
                    dfa_transitions.append(transition1)
                elif temp != []:
                    selected = Utils.select(dfa_states, temp)
                    if selected:
                        transition2 = TRANSITION(start=state.f, transition=symbol, end=selected.f)
                        dfa_transitions.append(transition2)
        
        #for transition in dfa_transitions:print('('+str(transition.start)+', '+transition.transition+', '+str(transition.end)+'), ') 
        
        afd_direct = AUTOMATON(dfa_states,"eval",symbols,None,acceptance_states,dfa_transitions)
        return afd_direct

    '''
    --------------- SUBSETS  ---------------
    '''
    @staticmethod
    def eclosure(step, transitions):
        #calculate all the epsilon transitions starting from a node or nodes
        if isinstance(step, int):
            nodes = []
            nodes.append(step)
        else: 
            nodes = list(step)
        if isinstance(nodes, list):
            for n in nodes:
                move = Utils.possible_movements(n, "ε", transitions)
                for x in move:
                    if int(x.end) not in nodes:
                        nodes.append(int(x.end))
        s = set()
        for item in nodes:
            s.add(item)
        return s
    
    @staticmethod
    def move(nodes, symbol, transitions):
        # Method to calculate the move starting from a node
        nodes = list(nodes)
        moves = []
        if isinstance(nodes, list):
            for n in range(len(nodes)):
                posible_moves = Utils.possible_movements(nodes[n], symbol, transitions)
                for move in posible_moves:
                    if str(move.end) not in moves:
                        moves.append(str(move.end))
            s = set()
            for item in moves:
                s.add(item)
            return s
        
        else:
            posible_moves = Utils.possible_movements(nodes, symbol, transitions)
            for move in posible_moves:
                if str(move.end) not in moves:
                    moves.append(str(move.end))
                    
            s = set()
            for item in moves:
                s.add(item)
            return s
        
    @staticmethod
    def possible_movements(node, symbols, transitions):
        # Shows possibles moves from a node and a symbol of the nfa
        moves = []
        for transition in transitions:
            if str(transition.start) == str(node) and str(transition.transition) == str(symbols):
                moves.append(transition) 
        return moves
    
    @staticmethod
    def subsets_algorithm(afn):
        # subset algorithm to convert nfa to dfa
        alphabet = afn.alphabet
        for character in alphabet:
            if character == "ε":
                alphabet.remove('ε')
        afn_pstates = [[int(afn.q0), int(afn.f)]]
                    
        i = 0
        dfa_state =[]
        table = []
        dfa_state.append(Utils.eclosure(int(afn.q0), afn.transitions))
        terminal_states =[]
        terminal_states.append(Utils.eclosure(int(afn.q0), afn.transitions))
        transitions_dfa = []
        
        while i < len(dfa_state):
            for n in alphabet:
                u = Utils.eclosure(Utils.move(dfa_state[i],n,afn.transitions),afn.transitions)
                transition = TRANSITION(start=dfa_state[i], transition=n, end=u)
                transitions_dfa.append(transition)
                if (transition.start != set() and transition.end != set()):
                    table.append(transition)
                for w in afn_pstates:
                    if w[1] in u:
                        terminal_states.append(u)
                if u not in dfa_state and u is not None and u != set():
                    dfa_state.append(u)         
            i+=1
            
        #for transition in table:print('('+str(transition.start)+', '+transition.transition+', '+str(transition.end)+'), ') 
        
        
        # assign a letter to each subset generated
        for transition in table:
            start1 = dfa_state.index(transition.start)
            h = DFA_ALPHABET_NODES[start1]
            transition.set_start(start=h)
            start2 = dfa_state.index(transition.end)
            n = DFA_ALPHABET_NODES[start2]
            transition.set_end(end=n)
        
        
        #for transition in table:print('('+str(transition.start)+', '+transition.transition+', '+str(transition.end)+'), ') 

        x = 0
        
        if len(terminal_states) <= 1:
            terminal_states.append(dfa_state[-1])

        while x < len(terminal_states):
            indice1 = dfa_state.index(terminal_states[x])
            terminal_states[x]= DFA_ALPHABET_NODES[indice1]
            x+=1
        
        acceptance_states = []
        for i in range(1, len(terminal_states)):
            acceptance_states.append(terminal_states[i])

        dfa = AUTOMATON(dfa_state, afn.expression, alphabet, terminal_states[0], acceptance_states, table)
        return dfa
    
    @staticmethod
    def unique(alphabet):
        return (list(set(alphabet)))
    '''
    --------------- THOMPSON  ---------------
    '''
    @staticmethod
    def thompson_algorithm(postfix):
        stack = []
        counter = 0

        for c in postfix:
            if (c != '(') and (c != ')')  and (c != '*') and (c != '|') and (c != '.'):
                #if the character to evaluate is not an operator we make a single transitions 
                #the transitions consist of two initial states and in the label the symbol we 
                #are evaluating 
                state1 = str(counter)
                state2 = str(counter+1)
                states = [state1, state2]
                counter+=2
                transition = TRANSITION(start=state1, transition=c, end=state2)
                transitions = [transition]
                element = AUTOMATON(q=states, expression=c, alphabet=[c], q0=state1, f=state2, transitions=transitions)
                stack.append(element)
            else:
                if (c == '|'):
                    #if the character to evaluate is the operator or we make the transitions epsilon
                    #with the states of the last two elementos

                    element2=stack.pop()
                    element1=stack.pop()
                    initial_state = str(counter)
                    final_state = str(counter+1)
                    counter+=2
                    transition1 = TRANSITION(start=initial_state, transition='ε', end=element1.q0)
                    transition2 = TRANSITION(start=initial_state, transition='ε', end=element2.q0)
                    transition3 = TRANSITION(start=element1.f, transition='ε', end=final_state)
                    transition4 = TRANSITION(start=element2.f, transition='ε', end=final_state)

                    old_transitions = element1.transitions + element2.transitions
                    new_transitions = [transition1, transition2, transition3, transition4]
                    current_transitions = old_transitions + new_transitions

                    old_states = element1.q + element2.q
                    new_states = [initial_state, final_state]
                    current_states = old_states + new_states

                    current_expression = '(' + element1.expression + '|' + element2.expression + ')'
                    current_alphabet = element1.alphabet + element2.alphabet

                    element = AUTOMATON(q=current_states, expression=current_expression, alphabet=current_alphabet, q0=initial_state, f=final_state, transitions=current_transitions)
                    stack.append(element)


                if (c == '.'):
                    #if the character to evaluate is the operator . we make the transitions epsilon
                    #with the states of the last two elementos
                    element2=stack.pop()
                    element1=stack.pop()

                    new_transitions = []
                    element2_transitions = []
                    
                    for transition in element2.transitions:
                        if transition.start == element2.q0:
                            transition1 = TRANSITION(start=element1.f, transition=transition.transition, end=transition.end)
                            new_transitions.append(transition1)
                        else:
                            element2_transitions.append(transition)    


                    old_transitions = element1.transitions + element2_transitions
                    current_transitions = old_transitions + new_transitions

                    old_states = element1.q + element2.q
                    current_states = []

                    for state in old_states:
                        if state != element2.q0:
                            current_states.append(state)

                    current_expression = '(' + element1.expression + '.' + element2.expression + ')'
                    current_alphabet = element1.alphabet + element2.alphabet        

                    element = AUTOMATON(q=current_states, expression=current_expression, alphabet=current_alphabet, q0=element1.q0, f=element2.f, transitions=current_transitions)
                    stack.append(element)

                if (c == '*'):
                    #if the character to evaluate is the operator kleen we make the transitions epsilon
                    #with the states of the last two elementos
                    element = stack.pop()
                    initial_state = str(counter)
                    final_state = str(counter+1)
                    counter+=2
                    transition1 = TRANSITION(start=initial_state, transition='ε', end=element.q0)
                    transition2 = TRANSITION(start=element.f, transition='ε', end=final_state)
                    transition3 = TRANSITION(start=initial_state, transition='ε', end=final_state)
                    transition4 = TRANSITION(start=element.f, transition='ε', end=element.q0)

                    old_transitions = element.transitions 
                    new_transitions = [transition1, transition2, transition3, transition4]
                    current_transitions = old_transitions + new_transitions

                    old_states = element.q 
                    new_states = [initial_state, final_state]
                    current_states = old_states + new_states

                    current_expression = '(' + element.expression + ')*'
                    current_alphabet = element.alphabet

                    element = AUTOMATON(q=current_states, expression=current_expression, alphabet=current_alphabet, q0=initial_state, f=final_state, transitions=current_transitions)
                    stack.append(element)
        
        #the last element in the stack is the final automata with all the "mini automatas" together

        last = stack.pop()
        #for state in last.q: print(state + ', ') 

        last.alphabet = Utils.unique(last.alphabet)
        #for char in last.alphabet:print(char + ', ')    

        #for transition in last.transitions:print('('+transition.start+', '+transition.transition+', '+transition.end+'), ') 
        return (last)
    '''
    Utils functions
    '''
    @staticmethod
    def generate_tree(expression):
        output = []
        stack = []
        i = 0

        while i < len(expression):        
            if expression[i] not in OPERATORS:
                val = ""
                while (i < len(expression)) and expression[i] not in OPERATORS:
                    val = str(val) + expression[i]
                    i -= -1
                tree = Tree()
                tree.symbol = val
                output.append(tree)
                i -= 1
            elif expression[i] == "(":
                stack.append(expression[i])
            elif expression[i] == ")":
                while len(stack) != 0 and stack[-1] != "(":
                    val2 = output.pop()
                    val1 = output.pop()
                    op = stack.pop()
                    tree = Tree()
                    tree.symbol = op
                    tree.left = val1
                    tree.right = val2
                    output.append(tree)
                stack.pop()
            
            else:
                if expression[i] == "*":
                    op = expression[i]
                    val = output.pop()
                    tree = Tree()
                    tree.symbol = op
                    tree.left = val
                    tree.right = None
                    output.append(tree)
                else:
                    while stack  and stack[-1] != '(':
                        op = stack.pop()
                        val2 = output.pop()
                        val1 = output.pop()
                        tree = Tree()
                        tree.symbol = op
                        tree.left = val1
                        tree.right = val2
                        output.append(tree)
                    stack.append(expression[i])
            
            i -= -1
        
        while stack:
            val2 = output.pop()
            val1 = output.pop()
            op = stack.pop()
            tree = Tree()
            tree.symbol = op
            tree.left = val1
            tree.right = val2
            output.append(tree)
            if (len(output) == 1):
                return output[-1]

        return output[-1]
    
    @staticmethod
    def precedence(operation):
        operation_hash = {
            '|': 1,
            '.': 2,
            '*': 3,
        }
        if operation in operation_hash:
            return operation_hash[operation]
        else:
            return 0
    
    @staticmethod
    def lock(afn, actual):
        for x in actual:
            for transition in afn.transitions:
                if transition.transition == "ε" and transition.end not in actual:
                    actual.append(transition.end)
        return actual
    
    @staticmethod
    def expand(expression):
        r = ""
        counter = 0
        for character in expression:
            if character == "|":
                counter = 0
            elif character == "(":
                if counter == 1 :
                    r = r + "." 
                    counter = 0
            elif character == ")" or character == "*" or character == ".":
                pass
            else:
                counter += 1
            if counter == 2:
                r = r + "." + character
                counter = 1
            else:
                r = r + character
        return r
    
    @staticmethod
    def parse_expresion(expression):
        # Method to substitute ? for |ε and a+ for aa*
        new = []
        stack = []
        for character in expression:
            #print(character)
            if character != "?" and character != "+":
                #print(character,expression)
                new.append(character)
                stack.append(character)
            elif character == "?":
                x = stack.pop()
                new.pop()
                new.append(str("("+x+"|ε)"))
                stack = []
            elif character == "+":
                #print(character,'entro',stack)
                x = stack.pop()
                if x == ")":
                    #print(stack)
                    y = stack.pop()
                    op = stack.pop()
                    v = stack.pop()
                    p = stack.pop()
                    final = p + v + op + y + x
                    new.append(str(final+"*"))
                else:
                    new.append(str("("+x+"*)"))    
        return ''.join(new)
    
    @staticmethod
    def infix_to_postfix(expression):
        # Method to pass infix expression to postfix
        stack = []
        output = []
        for character in expression:
            if character not in OPERATORS: 
                output.append(character)
            elif character == '(':
                stack.append(character)
            elif character == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                while stack and stack[-1] != '(' and Utils.precedence(character)<= Utils.precedence(stack[-1]):
                    output.append(stack.pop())
                stack.append(character)
        
        while stack:
            output.append(stack.pop())

        return output
    
    @staticmethod
    def is_balance(expression): 
        stack = [] 
        for i in expression: 
            if i in OPEN_LIST: 
                stack.append(i) 
            elif i in CLOSE_LIST: 
                pos = CLOSE_LIST.index(i) 
                if ((len(stack) > 0) and
                    (OPEN_LIST[pos] == stack[len(stack)-1])): 
                    stack.pop() 
                else: 
                    return False
        if len(stack) == 0: 
            return True
        else: 
            return False
    
    @staticmethod
    def graphic(afn,file_name,method):
        directory = './generated/'
        file_path = os.path.join(directory, file_name)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        f = Digraph('finite_state_machine', filename= file_path+'.png')
        f.attr(rankdir='LR', size='8,5')
        f.attr('node', shape='doublecircle')
        
        if method.upper() == 'AFN':
            f.node(afn.q0)
            f.node(afn.f)
        elif method.upper() == 'AFD' or method.upper() == 'DIRECT':
            for node in afn.f:
                f.node(str(node))
        
        f.attr('node', shape='circle')
        for transition in afn.transitions:
            f.edge(str(transition.start), str(transition.end), label=str(transition.transition))
        f.view()
    
    @staticmethod
    def write_txt_file(file_name,afn):
        directory = './generated/'
        file_path = os.path.join(directory, file_name)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        f = open(file_path+'.txt', 'w+', encoding="utf-8")
        f.write("Estados = {")
        for state in afn.q: 
            f.write(str(state) + ',') 
        f.write("}")
        f.write('\n')
        f.write("Simbolos = {")
        for char in afn.alphabet:
            f.write(str(char) + ',')
        f.write("}")    
        f.write('\n')
        
        f.write("Inicio: " + str(afn.q0)) 
        f.write('\n')

        f.write("Aceptacion: " + str(afn.f)) 
        f.write('\n') 

        f.write("Transiciones: ")
        f.write('\n')
        for transition in afn.transitions:
            f.write('('+str(transition.start)+', '+str(transition.transition)+', '+str(transition.end)+'), ')
            
    @staticmethod
    def simulate(expression,afn=None,transitions=None, inicial_node=None, acceptance_states=None):
        if afn is not None:
            if expression == " ":
                expression = "ε"
            actual = [afn.q0]
            actual = Utils.lock(afn, actual)
            i = 0
            while True:
                temp = []
                for node in actual:
                    for transition in afn.transitions:
                        if transition.transition == expression[i] and transition.end not in temp:
                            temp.append(transition.end)
                i += 1
                temp = Utils.lock(afn, temp)
                if not temp and expression == "ε":
                    break
                actual = temp.copy()
                if i > len(expression)-1:
                    break
            for x in actual:
                if x == afn.f:
                    return True
            return False
        else:
            #checking that all transitions are not None
            if transitions is None or inicial_node is None or acceptance_states is None:
                return False
            i = 0
            inicial = inicial_node
            
            for character in expression:
                x = Utils.move(inicial, character, transitions)
                if len(x)==0:
                    return False
                x = list(x)
                inicial = x[0]
            i = 0 
            for n in range(len(acceptance_states)):
                if inicial == acceptance_states[n]:
                    i += 1
            if i !=0:
                return True
            else:
                return False
            
    @staticmethod
    def get_infix_expression():
        expression = input('Enter infix expression: ')
        #expression = expression.replace('ε','ε')
        balanced = Utils.is_balance(expression)
        return expression,balanced