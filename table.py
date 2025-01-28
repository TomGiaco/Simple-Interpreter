
####################
#       IMPORTS
####################

import re
import itertools
import fileinput

###################################################
#                   UTILS
###################################################


# Rules of tokenization
Lexic = {'(',')','=','var', 'show', 'show_ones','not','and','or','True','False',';'}
Lexic_eq = {'(',')','not','and','or','True','False'}

# Check that variable respect rules imposed and is not a keyword
def check_id(word):
    return (re.match(r'^[A-Za-z_]\w*$', word) is not None) and word not in Lexic

# Used to divide into sublist and to check them singularly
def split_by_semicolumn(l):
    new_list = []
    sublist = []
    for words in l:
        sublist.append(words)
        if words == ";":
            new_list.append(sublist)
            sublist = []
    return new_list

# Function to check if there are all and or all or
def check_which_and_or(words):
    if all(word == 'or' for word in words[1::2]):
        return 'or'
    if all(word == 'and' for word in words[1::2]):
        return 'and'
    return None

#########################################
#            ERRORS
######################################

class FormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.message}"
    
class LexicalError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.message}"
   



###########################################################################
#             MAIN FUNCTIONS AND CLASSES
##########################################################################


###############################
#          TOKENIZATION
###############################

def open_and_tokenize():

    file = []
    
    # Check if the file is format '.txt'
    if '.txt' not in fileinput.input()._files[0]:
        raise FileNotFoundError("You must provide a .txt file!")
    # Use fileinput to read the file
    for line in fileinput.input():
        # Remove comments
        no_comm = line.split('#')[0].strip()  
        if no_comm:
            # Find all the words
            words = re.findall(r'\w+|[^\s\w]', no_comm)
            file.extend(words)
    
    if len(file) == 0:
        raise FormatError("You inserted an empty file!")
    
    # check syntax
    for i in range(len(file)):
        word = file[i]
        if word in Lexic:
            continue
        elif check_id(word):
            file[i] = word
        else:
            raise LexicalError('This synatx is not accepted')   
        
    return split_by_semicolumn(file)

def generate_truth_combinations(variables):
    constants = {'True': True, 'False': False}
    return [{**dict(zip(variables, combo)), **constants} for combo in itertools.product([False, True], repeat=len(variables))]

##############################################
#               CHECKS
###############################################

def check_assignment(li,vars):

    # Check syntax
    if li[0] == 'var':
        # Append the variables
        vars.extend([item for item in li[1:-1] if check_id(item)])
        # If same variables are defined or some are not accepted
        if len(vars) > 64 or len(vars) > len(set(vars)) or len(vars) < len(li) -2:
            raise LexicalError("Variables erroneously defined!")
        return True
    else:
        return False

def check_eq(li,vars):
    # Check first synatx
    if check_id(li[0]) and (li[0] not in vars) and li[1] == '=':
        # all admissiable charachters and existing variables
        eq = li[2:-1]
        # Stack for checking parenthesis
        for words in eq :
            if (words not in vars) and (words not in Lexic_eq):
                raise LexicalError("This characther is not defined")
        # Now try evaluating with all False and see if it raises some errors
        values = {v:False for v in vars}
        values['True'] = True
        values['False'] = False
        try:
            eval_equation(values,eq)
        except:
            raise LexicalError("Lexic error in the equation")
        
        return True
    else:
        return False

# For short circuiting
def check_parentesis_removal(li, vars):
    if li[0] == '(' and li[-1] == ')':
        eq = li[3:-2]
        # Now try evaluating with all False and see if it raises some errors
        values = {v:False for v in vars}
        values['True'] = True
        values['False'] = False
        try:
            eval_equation(values,eq)
        except:
            return False
        
        return True
    else:
        return False

def check_show(li,tar):

    if (li[0] == 'show' or li[0] == 'show_ones') and li[-1] == ';':
        for words in li[1:-1]:
            if words not in tar:
                raise LexicalError("Variable not defined by assignment")
        if len(li[1:-1]) == 0:
            raise LexicalError("No argument to print!")
        return True
    else:
        return False

#####################################
#  DISJUNCTION CONJUNCTION NEGATIONS
#####################################

def disj_conj_neg_id(vars,z):

    # Negation
    if z[0] == 'not':
        return ('neg',z)
    
    # Disjunction or Conjunction
    else:
        stack = []
        excluded = set()
        new_z = []
        counter = 0
        while counter < len(z):
            # Two cases:
            # 1. single variables
            # 2. parenthesis variables
            curr = z[counter]
            if (not stack) and (curr in vars or (curr in ['True','False'])):
                new_z.append(curr)
                counter += 1
            elif curr == '(':
                stack.append('(')
                sub_expr = [curr]
                counter += 1
                
                while stack:
                    curr2 = z[counter]
                    sub_expr.append(curr2)
                    if curr2 == '(':
                        stack.append('(')  
                    elif curr2 == ')':
                        stack.pop()  
                    counter += 1
                new_z.append(sub_expr)
            else:
                excluded.add(curr)
                counter += 1

        if 'and' in excluded:
            return ('conj',new_z)
        else:
            return ('disj',new_z) 


#######################################
#           RECURSION EVALUATION
#######################################


# Go along the equation and if u find a parenthesis take the whole block and evaluate that
def eval_equation(val,expr):
    
    if len(expr) == 1:
        return str(val[expr[0]])
    elif len(expr) == 2 and expr[0] == 'not':
        return str(not(val[expr[1]]))
    elif check_which_and_or(expr) == 'and':
        return str(all(val.get(e, False) for e in expr if e != 'and'))  
    elif check_which_and_or(expr) == 'or':
        return str(any(val.get(e, False) for e in expr if e != 'or'))
    else:
        stack = []
        for token in expr:
            if token == ')':
                sub_expr = []
                while stack and stack[-1] != '(':
                    sub_expr.insert(0, stack.pop())
                stack.pop() 
                # Recursively evaluate the sub-expression
                stack.append(eval_equation(val, sub_expr))
            else:
                stack.append(token)

        return eval_equation(val, stack)

def eval_disjunction_or_conjunction(val,id,new_z):

    if id == 'conj':
        for i in new_z:
            if isinstance(i,str) and (not val[i]):
                return 'False'
            elif isinstance(i,list) and not eval(eval_equation(val,i)):
                return 'False'
        return 'True'
    
    elif id == 'disj':
        for i in new_z:
            if isinstance(i,str) and val[i]:
                return 'True'
            elif isinstance(i,list) and eval(eval_equation(val,i)):
                return 'True'
        return 'False'
    
    else:
        return eval_equation(val,new_z)
    

    
###########################################
#                TRUTH TABLE PRINTING
###########################################

def truth_table_real(vars, values, expr, li):

    if li[0] == 'show':
        targets = li[1:-1]
        var_by_ass = [v for v in vars if v not in list(expr.keys())]

        # Determine the width for each variable name
        max_var_length = max(len(var) for var in var_by_ass)
        max_tar_length = max(len(var) for var in targets)

        header = ' '.join([f'{var:>{max_var_length}}' for var in var_by_ass]) + '  ' + ' '.join(targets)
        print(f"# {header}")

        comb = generate_truth_combinations(var_by_ass)

        for combinations in comb:
            try:
                evaluations = [eval_disjunction_or_conjunction(combinations, expr[tar][0], expr[tar][1]) for tar in targets]
            except:
                raise LexicalError('Invalid syntax')

            if None in evaluations:
                raise LexicalError('Invalid syntax')

            # Put values of variables with alignment
            ass_str = ' '.join([f"{'1' if combinations[var_val] else '0':>{max_var_length}}" for var_val in var_by_ass])
            eq_str = ' '.join([f"{'1' if values[e] else '0':>{max_tar_length}}" for e in evaluations])

            # Print truth table with aligned values
            print(f"  {ass_str}"+ ' ' + f" {eq_str}")

    elif li[0] == 'show_ones':

        targets = li[1:-1]
        var_by_ass = [v for v in vars if v not in list(expr.keys())]

        # Determine the width for each variable name
        max_var_length = max(len(var) for var in var_by_ass)
        max_tar_length = max(len(var) for var in targets)

        # Create the header with appropriate spacing
        header = ' '.join([f'{var:>{max_var_length}}' for var in var_by_ass]) + '  ' + ' '.join(targets)
        print(f"# {header}")

        comb = generate_truth_combinations(var_by_ass)

        for combinations in comb:
            try:
                evaluations = [eval_disjunction_or_conjunction(combinations, expr[tar][0], expr[tar][1]) for tar in targets]
            except:
                raise LexicalError('Invalid syntax')

            if None in evaluations:
                raise LexicalError('Invalid syntax')

            # Don't print all zeros
            if 'True' not in evaluations:
                continue
            
            # Put values of variables with alignment
            ass_str = ' '.join([f"{'1' if combinations[var_val] else '0':>{max_var_length}}" for var_val in var_by_ass])
            eq_str = ' '.join([f"{'1' if values[e] else '0':>{max_tar_length}}" for e in evaluations])

            # Print truth table with aligned values
            print(f"  {ass_str}"+ ' ' + f" {eq_str}")






######################################
#            GENERAL
#######################################

def general(tokens):

    # Initialization
    vars = [] # List of declared variables
    values = {'True':True,'False':False} 
    expr = {} # Dict with target variable as key and his expression as value
    opt_expr = {}
    # Iterate trough the tokens
    for lines in tokens:
        # If assignment
        if check_assignment(lines,vars):
            # This function extend vars with the one declared
            continue
        # If expression
        elif check_eq(lines,vars) and (not check_parentesis_removal(lines,vars)):
            expr[lines[0]] = lines[2:-1]
            name = lines[0]
            vars.append(name)
            li = list(expr.keys())
            # Substitute in case there are variables defined in assignments in other assignments
            for d1 in li[:-1]:
                d2 = li[-1]
                new_expr = []
                for element in expr[d2]:
                    if element == d1: 
                        new_expr.extend(['('] + expr[d1] + [')'])
                    else:
                        new_expr.append(element)
                    expr[d2] = new_expr
            
            id_cd, new_z = disj_conj_neg_id(vars,expr[name])
            opt_expr[name] = (id_cd,new_z)

        elif check_eq(lines,vars) and (check_parentesis_removal(lines,vars)):
            expr[lines[0]] = lines[3:-2]
            name = lines[0]
            vars.append(name)
            li = list(expr.keys())
            # Substitute in case there are variables defined in assignments in other assignments
            for d1 in li[:-1]:
                d2 = li[-1]
                new_expr = []
                for element in expr[d2]:
                    if element == d1: 
                        new_expr.extend(['('] + expr[d1] + [')'])
                    else:
                        new_expr.append(element)
                    expr[d2] = new_expr
            id_cd, new_z = disj_conj_neg_id(vars,expr[name])
            opt_expr[name] = (id_cd,new_z)

        elif check_show(lines,list(expr.keys())):
            truth_table_real(vars,values,opt_expr,lines)
        else:
            raise LexicalError('Syntax not defined')       
        
    
                    
if __name__ == "__main__":
    tokens = open_and_tokenize()
    general(tokens)