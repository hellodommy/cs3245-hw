from nltk.stem.porter import *
import math

def tokenize(word):
    '''
    Tokenises a given word with Porter Stemmer and case folding
    '''
    word = word.lower()
    word = PorterStemmer().stem(word)
    return word

def add_skip_ptr(posting_list):
    '''
    Returns a string form of posting list with skip pointers, indicated by carat
    '''
    l = len(posting_list)
    result = ''
    if l > 2:
        num_ptr = math.floor(math.sqrt(l))
        ptr_gap = math.floor(l / num_ptr)
        for i in range(l):
            if i % ptr_gap == 0 and i < l - 2:
                if i + ptr_gap >= l:
                    result += str(posting_list[i]) + \
                        ' ^' + str(l - i - 1) + ' '
                else:
                    result += str(posting_list[i]) + ' ^' + str(ptr_gap) + ' '
            else:
                result += str(posting_list[i]) + ' '
    else:
        for i in range(l):
            result += str(posting_list[i]) + ' '
    return result

def list_to_string(my_list):
    '''
    Stringifies and concatenates (with a space between) the elements of the given list
    '''
    res = ''
    for l in my_list:
        res += str(l) + ' '
    return res

def split_bool_expr(expression):
    '''
    Splits given boolean string expression into string list of operators and operands

    Operators handled: AND, OR, NOT, ()

    Assumptions: no nested (); expression is valid
    '''
    initial_split = expression.split()
    final_split = []
    for item in initial_split:
        if item[0] == "(" and item[-1] == ")":
            final_split.extend(["(", item[1:-1], ")"])
        elif item[0] == "(":
            final_split.extend(["(", item[1:]])
        elif item[len(item) - 1] == ")":
            final_split.extend([item[:-1], ")"])
        else:
            final_split.append(item)

    return final_split

def has_greater_or_equal_precedence(op1, op2):
    '''
    Returns true if `op1` has greater than or equal precedence to `op2`. False otherwise.

    Operators handled (decreasing precedence): AND, OR
    '''
    return (op1 == "AND" and op2 == "OR") or op1 == op2

def infix_to_postfix(expression):
    '''
    Translates string infix boolean expression to string list postfix boolean expression

    Operators handled: AND, OR, NOT, ()

    Assumptions: no nested (); expression is valid
    '''
    split_expr = split_bool_expr(expression)
    output_queue = [] # first in, first out
    operator_stack = [] # last in, first out
    unary_list = []

    # use Shunting-Yard algorithm, with modifications to handle NOT unary operator
    for item in split_expr:
        if item == "NOT":
            unary_list.append(item)
        elif item == "AND" or item == "OR":
            while len(operator_stack) > 0 and has_greater_or_equal_precedence(operator_stack[-1], item) and operator_stack[-1] != "(":
                output_queue.append(operator_stack.pop())
            operator_stack.append(item)
        elif item == "(":
            operator_stack.append(item)
            if len(unary_list) > 0:
                unary_list.append(item)
        elif item == ")":
            while operator_stack[-1] != "(":
                output_queue.append(operator_stack.pop())
            if operator_stack[-1] == "(":
                operator_stack.pop()
            if len(unary_list) > 0 and unary_list[-1] == "(":
                unary_list.pop()
                while len(unary_list) > 0 and unary_list[-1] != "(":
                    output_queue.append(unary_list.pop())
        else:
            # item is an operand
            output_queue.append(item)
            if len(unary_list) > 0:
                while len(unary_list) > 0 and unary_list[-1] != "(":
                    output_queue.append(unary_list.pop())
    
    for operator in reversed(operator_stack):
        output_queue.append(operator)
    
    return output_queue
