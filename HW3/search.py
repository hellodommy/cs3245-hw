#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import math
from collections import Counter
from data import set_postings_file, read_dict, get_corpus_size, get_doc_id_len_pairs, get_postings_list, get_doc_ids, get_doc_freq
from utility import list_to_string
import heapq as hq

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
        curated_docs = curate_doc_scores(doc_scores)

        if curated_docs[0][1] == 0:
            if i == len(lines) - 1:
                rf.write('')
            else:
                rf.write('\n')
        else:
            for j in range(10):
                if j == len(curated_docs) - 1:
                    rf.write(str(curated_docs[j][0]))
                else:
                    rf.write(str(curated_docs[j][0]) + ' ')
            if i != len(lines) - 1:
                rf.write('\n')
    
    rf.close()

def calculate_tfidf_query(term, term_freq_in_query, corpus_size):
    if term_freq_in_query == 0:
        return 0
    doc_freq = get_doc_freq(term)
    if doc_freq == 0:
        return 0
    
    tf = 1 + math.log(term_freq_in_query, 10)
    idf = math.log(corpus_size / doc_freq, 10)
    return tf * idf

def calculate_tfidf_documents(term, term_freq):
    if term_freq == 0:
        return 0
    
    tf = 1 + math.log(term_freq, 10)
    # idf not calculated for documents
    return tf

def calculate_cosine_scores(query):
    '''
    Returns a `scores` dictionary where the keys are doc IDs and the values are the cosine scores
    '''
    corpus_size = get_corpus_size()
    doc_id_len_pairs = get_doc_id_len_pairs()
    scores = dict(zip(get_doc_ids(), [0] * corpus_size))
    
    query_terms = query.split(' ')
    query_terms_counts = Counter(query_terms)
    for query_term in query_terms:
        weight_tq = calculate_tfidf_query(query_term, query_terms_counts[query_term], corpus_size)
        postings_list = get_postings_list(query_term)
        for (doc_id, term_freq) in postings_list:
            scores[doc_id] += weight_tq * calculate_tfidf_documents(query_term, term_freq)
    
    # normalize lengths
    for doc_id, score in scores.items():
        scores[doc_id] = score / doc_id_len_pairs[doc_id]
    
    return scores


def curate_doc_scores(scores):
    '''
    Returns the top 10 scoring documents using a max heap
    '''
    heap = [(-value, key) for key, value in scores.items()]
    largest = hq.nsmallest(10, heap)
    largest = [(key, -value) for value, key in largest]

    return largest

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
