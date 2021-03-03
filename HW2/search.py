#!/usr/bin/python3
import re
import string
import sys
import getopt
from data import set_postings_file, read_dict
from infix_optimizer import optimize_infix
from eval import evaluate_postfix
from utility import add_skip_ptr, list_to_string, tokenize, infix_to_postfix

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
    set_postings_file(postings_file)
    read_dict(dict_file) # read from dictionary file and store in memory
    queries = open(queries_file, 'r')
    rf = open(results_file, 'w+')
    rf.close()
    lines = queries.readlines()
    for i in range(len(lines)):
        rf = open(results_file, 'a')
        try:
            infix_query = lines[i].rstrip()
            optimized_infix = optimize_infix(infix_query)
            postfix_query = infix_to_postfix(optimized_infix)
            res = evaluate_postfix(postfix_query)
            if res == '':
                rf.write('\n')
            else:
                if i == len(lines) - 1:
                    rf.write(res)
                else:
                    rf.write(res + '\n')
        except AssertionError as error:
            # assertion error in evaluate_postfix() when there is no query, final stack will be empty
            rf.write('\n')
    rf.close()

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
