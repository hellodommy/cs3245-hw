#!/usr/bin/python3
import re
#import nltk
import string
import sys
import getopt
from queue import Queue

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
        tokenized = tokenize_query(query.rstrip())
        print(' '.join(list(tokenized.queue)))

def tokenize_query(query):
    split_query = query.split(' ')
    operator_stack = []
    output_queue = Queue()
    for item in split_query:
        if item.islower():
            # check for opening bracket
            if item[0] == '(':
                operator_stack.append('(')
                output_queue.put(item[1:])
            elif item[len(item) - 1] == ')':
                while len(operator_stack) > 0 and operator_stack[0] != '(':
                    output_queue.put(operator_stack.pop())
                if len(operator_stack) > 0 and operator_stack[0] == '(':
                    operator_stack.pop()
                else:
                    raise ValueError("cannot find matching open parenthesis with close")
            else:
                output_queue.put(item)
        elif item.isupper() and item in OPERATORS: # '(' will not get through here
            while((len(operator_stack) > 0) and (take_precedence(operator_stack[0], item) and operator_stack[0] != '(')):
                output_queue.put(operator_stack.pop())
            operator_stack.append(item)
        else:
            raise ValueError("we screqwed up")
    while len(operator_stack) > 0:
        output_queue.put(operator_stack.pop())
    return output_queue

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
