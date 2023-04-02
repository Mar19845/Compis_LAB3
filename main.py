from utils import Utils
import re
from models import *
from constants import *
import uuid

flag = True
while flag:
    print("1. Thompson Algorithm\n2. AFD Subconjuntos\n3. AFD Directo\n4. Exit")
    opc=input("Choose an option: ")
    
    if opc == '4':
        exit()
    elif opc == '1':
        expression,balanced = Utils.get_infix_expression()
        
        if balanced is True:
            expression = Utils.parse_expresion(expression) 
            expanded_expression = Utils.expand(expression)
            postfix_expression = Utils.infix_to_postfix(expanded_expression)
            
            afn = Utils.thompson_algorithm(postfix_expression)
            file_name = str(uuid.uuid4().fields[-1])[:5]
            Utils.write_txt_file(file_name,afn)
            Utils.graphic(afn,file_name,method='AFN')
            
            evaluation_exp = input('Expression to evaluate: ')
            state = Utils.simulate(evaluation_exp,afn=afn)
            if state is True:
                print('The expression: ' + str(evaluation_exp) + ' is valid \n')
            else:
                print('The expression: ' + str(evaluation_exp) + ' is not valid \n')
        else:
            print('Error in the expression: ' +str(expression) + '\n')
    elif opc == '2':
        expression,balanced = Utils.get_infix_expression()
        if balanced is True:
            expression = Utils.parse_expresion(expression) 
            expanded_expression = Utils.expand(expression)
            postfix_expression = Utils.infix_to_postfix(expanded_expression)
            afn = Utils.thompson_algorithm(postfix_expression)
            dfa = Utils.subsets_algorithm(afn)
            file_name = str(uuid.uuid4().fields[-1])[:5]
            Utils.write_txt_file(file_name,dfa)
            Utils.graphic(dfa,file_name,method='AFD')
            evaluation_exp = input('Expression to evaluate: ')
            state = Utils.simulate(evaluation_exp,transitions=dfa.transitions,inicial_node=dfa.q0,acceptance_states=dfa.f)
            if state is True:
                print('The expression: ' + str(evaluation_exp) + ' is valid \n')
            else:
                print('The expression: ' + str(evaluation_exp) + ' is not valid \n')
        else:
            print('Error in the expression: ' +str(expression) + '\n')
            
    elif opc == '3':
        expression,balanced = Utils.get_infix_expression()
        if balanced is True:
            expression = Utils.parse_expresion(expression) 
            expanded_expression = Utils.expand(expression)
            tree = Utils.generate_tree(expanded_expression)
            dfa = Utils.directo(tree,expanded_expression)
            file_name = str(uuid.uuid4().fields[-1])[:5]
            Utils.write_txt_file(file_name,dfa)
            Utils.graphic(dfa,file_name,method='AFD')
            evaluation_exp = input('Expression to evaluate: ')
            state = Utils.simulate(evaluation_exp,transitions=dfa.transitions,inicial_node=dfa.q0,acceptance_states=dfa.f)
            if state is True:
                print('The expression: ' + str(evaluation_exp) + ' is valid \n')
            else:
                print('The expression: ' + str(evaluation_exp) + ' is not valid \n')
        else:
            print('Error in the expression: ' +str(expression) + '\n')
    elif opc !="":
      print("\nWrong option") 