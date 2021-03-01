#!/usr/bin/python3
import re
import string
import sys
import getopt
from nltk.stem.porter import *

OPERATORS = ['(', 'NOT', 'AND', 'OR']
DICTIONARY = {}
POSTINGS_FILE = ''

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

# TODO: Find a way to reuse the tokenize method from index.py without fking up the usage instructions
def tokenize(word):
    stemmer = PorterStemmer()
    word = word.lower()
    word = stemmer.stem(word)
    return word

def read_dict(dict_file):
    global DICTIONARY
    f = open(dict_file, 'r')
    for line in f.readlines():
        info = (line.rstrip()).split(' ')
        # term: [doc_freq, absolute_offset, accumulative_offset]
        DICTIONARY[info[0]] = [int(info[1]), int(info[2]), int(info[3])]
    f.close()

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    global POSTINGS_FILE
    read_dict(dict_file) # read from dictionary file and store in memory
    POSTINGS_FILE = postings_file
    queries = open(queries_file, 'r')
    for query in queries.readlines():
        postfix_query = infix_to_postfix(query.rstrip())
        res = evaluate_postfix(postfix_query)
        print(res)
        #print(' '.join(postfix_query))

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
        elif item == "AND":
            # apply AND/OR operator to popped operands
            # push result back onto stack
            res = eval_AND(stack.pop(), stack.pop())
            stack.append(res)
        elif item == "OR":
            operand_one = stack.pop()
            operand_two = stack.pop()
        else:
            # item is an operand
            stack.append(item)
    
    # stack will only have one item now: the final result
    assert len(stack) == 1
    return stack.pop()

def read_posting(seek_offset, bytes_to_read):
    f = open(POSTINGS_FILE, 'r')
    result = ''
    f.seek(seek_offset)
    result += f.read(bytes_to_read)
    f.close()
    return result


def get_skip(posting_list):
    skip_list = []
    reg_list = []
    posting_count = 0
    items = posting_list.rstrip().split(' ')
    item_count = 0
    while (item_count < len(items)):
        reg_list.append(int(items[item_count]))
        if item_count < len(items) - 1 and (items[item_count + 1][0] == '^'):
            skip_dist = int(items[item_count + 1][1:])
            skip_list.append(posting_count + skip_dist)
            item_count += 2  # move past the skip ptr
            posting_count += 1
        else:
            # there is no skip ptr assigned to this element
            skip_list.append(None)
            item_count += 1
            posting_count += 1
    assert len(reg_list) == len(skip_list)

    return reg_list, skip_list

def eval_AND(op1, op2):
    '''
    assume no skip pointers
    '''
    tok1 = tokenize(op1)
    tok2 = tokenize(op2)
    off1, bytes1 = DICTIONARY[tok1][1], DICTIONARY[tok1][2]
    off2, bytes2 = DICTIONARY[tok2][1], DICTIONARY[tok2][2]
    bytes1 = read_posting(off1, bytes1)
    posting1, skips1 = get_skip(bytes1)
    bytes2 = read_posting(off2, bytes2)
    posting2, skips2 = get_skip(bytes2)
    ptr1 = 0
    ptr2 = 0
    result = ''
    while ptr1 < len(posting1) and ptr2 < len(posting2):
        if posting1[ptr1] == posting2[ptr2]:
            result += str(posting1[ptr1]) + ' '
            ptr1 += 1
            ptr2 += 1
        elif posting1[ptr1] > posting2[ptr2]:
            if skips2[ptr2] is not None and posting2[skips2[ptr2]] <= posting1[ptr1]:
                ptr2 = skips2[ptr2]
            else:
                ptr2 += 1
        elif posting2[ptr2] > posting1[ptr1]:
            if skips1[ptr1] is not None and posting1[skips1[ptr1]] <= posting2[ptr2]:
                ptr1 = skips1[ptr1]
            else:
                ptr1 += 1
    return result

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
