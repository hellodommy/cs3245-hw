#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from data import set_postings_file, read_dict, get_corpus_size, get_doc_lengths, get_postings_list, get_doc_ids
from utility import list_to_string

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

    rf = open(results_file, 'w+')
    rf.close()

    queries = open(queries_file, 'r')
    lines = queries.readlines()

    for i in range(len(lines)):
        rf = open(results_file, 'a')
        query = lines[i].rstrip()
        doc_scores = calculate_cosine_scores(query)
        curated_docs = curate_doc_scores(doc_scores, 10)
        string_result = list_to_string(curated_docs)
        if string_result == '':
            if i == len(lines) - 1:
                rf.write('')
            else:
                rf.write('\n')
        else:
            if i == len(lines) - 1:
                rf.write(string_result)
            else:
                rf.write(string_result + '\n')
    
    rf.close()

def calculate_tfidf_query(query_term):
    # TODO: implement
    return 1

def calculate_tfidf_documents(term):
    # TODO: implement
    return 1

def calculate_cosine_scores(query):
    '''
    Returns a `scores` dictionary where the keys are doc IDs and the values are the cosine scores
    '''
    corpus_size = get_corpus_size()
    doc_lengths = get_doc_lengths()
    scores = dict(zip(get_doc_ids(), [0] * corpus_size))
    for query_term in query.split(' '):
        weight_tq = calculate_tfidf_query(query_term)
        postings_list = get_postings_list(query_term)
        for (doc_id, term_freq) in postings_list:
            scores[doc_id] += weight_tq * calculate_tfidf_documents(query_term)
    # normalize lengths
    for doc_id, score in scores.items():
        scores[doc_id] = score / doc_lengths[doc_id]
    return scores

def curate_doc_scores(doc_scores, limit):
    '''
    Returns a list of length `limit` of doc IDs, sorted by score in descending order
    '''
    sorted_doc_ids = dict(sorted(doc_scores.items(), key = lambda doc_score: doc_score[1], reverse = True)).keys()
    return sorted_doc_ids[:limit]

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
