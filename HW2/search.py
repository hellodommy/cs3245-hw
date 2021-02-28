#!/usr/bin/python3
import re
#import nltk
import string
import sys
import getopt

OPERATORS = ['(', 'NOT', 'AND', 'OR']

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    queries = open(queries_file, 'r')
    for query in queries.readlines():
        postfix_query = infix_to_postfix(query.rstrip())
        print(' '.join(postfix_query))

def split_bool_expr(expression):
    '''
    Splits given boolean string expression into string list of operators and operands
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

def infix_to_postfix(expression):
    '''
    Translates string postfix boolean expression to string list infix boolean expression
    Operators handled: AND, OR, NOT, ()
    Assumptions: no nested (); expression is valid
    '''
    split_expr = split_bool_expr(expression)
    output_queue = [] # first in, first out
    operator_stack = [] # last in, first out
    unary_list = []
    for item in split_expr:
        if item == "NOT":
            unary_list.append(item)
        elif item == "AND" or item == "OR":
            while ((len(operator_stack) > 0 and (operator_stack[-1] == "AND" or operator_stack[-1] == "OR")) and operator_stack[-1] == item and operator_stack[-1] != "("):
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
            if unary_list[-1] == "(":
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

def evaluate_postfix(postfix_expr):
    '''
    Evaluates the given string list postfix expression
    '''
    stack = [] # last in, first out
    for item in postfix_expr:
        if item == "NOT":
            operand = stack.pop()
            # apply NOT operator to popped operand
            # push result back onto stack
        elif item == "AND" or item == "OR":
            operand_one = stack.pop()
            operand_two = stack.pop()
            # apply AND/OR operator to popped operands
            # push result back onto stack
        else:
            # item is an operand
            stack.append(item)
    
    # stack will only have one item now: the final result
    return stack.pop()

def take_precedence(op1, op2):
    return OPERATORS.index(op1) <= OPERATORS.index(op2)

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
