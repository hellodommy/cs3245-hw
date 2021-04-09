#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import math
from collections import Counter
from nltk import ngrams
from data import set_postings_file, read_dict, get_corpus_size, get_doc_id_len_pairs, get_postings_list, get_doc_ids, get_doc_freq, get_main_posting_list
import heapq as hq

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    '''
    Uses the given dictionary file and postings file
    to perform searching on the given queries file and
    output the results to a file
    '''
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    set_postings_file(postings_file)
    read_dict(dict_file) # read from dictionary file and store in memory

    rf = open(results_file, 'w+')
    rf.write('')
    rf.close()

    queries = open(queries_file, 'r')
    lines = queries.readline()

    queries = open(queries_file, 'r')
    line = queries.readline()

    rf = open(results_file, 'a')
    query = line.rstrip()
    doc_scores = calculate_cosine_scores(query)
    result_docs = [k for k, v in sorted(doc_scores.items(), key=lambda item: (-item[1], item[0]))]

    for i in range(len(result_docs)):
        if i == len(result_docs) - 1:
            rf.write(str(result_docs[i]))
        else:
            rf.write(str(result_docs[i]) + ' ')

    rf.close()


def parse_query(query):
    parsed_terms = []

    '''a ha ah "This is hot" AND "This is cold"
    [[a,ha,ah,"This,is,hot"], ["This,is,cold"]]
    [[a, ha, ah, this is hot], [this is cold]]'''

    query_terms = [term.split(' ') for term in query.split(' AND ')]
    is_quote = False
    for segment in query_terms:
        segment_terms = []
        quote = ""
        for i in range(len(segment)):
            if segment[i].startswith('"') and segment[i].endswith('"'):
                segment_terms.append(segment[i].strip('"'))
            elif segment[i].startswith('"'):
                is_quote = True
                quote += segment[i].strip('"') + " "
            elif segment[i].endswith('"'):
                is_quote = False
                quote += segment[i].strip('"')
                segment_terms.append(quote)
                quote = ""
            elif not is_quote:
                segment_terms.append(segment[i])
            else:
                quote += segment[i] + " "
        parsed_terms.append(segment_terms)

    return parsed_terms


def calculate_tfidf_query(term, term_freq_in_query, corpus_size):
    '''
    Calculates the tf-idf (ltc) for a query
    '''
    if term_freq_in_query == 0:
        return 0
    doc_freq = get_doc_freq(term)
    if doc_freq == 0:
        return 0

    tf = 1 + math.log(term_freq_in_query, 10)
    idf = math.log(corpus_size / doc_freq, 10)
    return tf * idf

def calculate_tfidf_documents(term, term_freq):
    '''
    Calculates the tf-idf (lnc) for a document
    '''
    if term_freq == 0:
        return 0

    tf = 1 + math.log(term_freq, 10)
    # idf not calculated for documents
    return tf

def add_to_count(term, dictionary):
    if term in dictionary:
        dictionary[term] += 1
    else:
        dictionary[term] = 1

def counter(query_terms):
    count_dict = {}
    for segment in query_terms:
        for term in segment:
            split_term = term.split(' ')
            if len(split_term) == 3:
                for item in list(ngrams(split_term, 2)):
                    to_add = item[0] + " " + item[1]
                    add_to_count(to_add, count_dict)
            else:
                add_to_count(term, count_dict)
    return count_dict


#modify this
def calculate_cosine_scores(query):
    '''
    Returns a `scores` dictionary where the keys are doc IDs and the values are the cosine scores
    '''
    corpus_size = get_corpus_size()
    doc_id_len_pairs = get_doc_id_len_pairs()
    scores = dict(zip(get_doc_ids(), [0] * corpus_size))

    query_terms = parse_query(query)
    query_terms_counts = counter(query_terms)
    #get all the posting list include combine and that all
    #[[ha, ah, ha2, This is cold], [This is hot]]
    #[1,2,3,4,5,6]
    main_posting_list = get_main_posting_list(query_terms);
    # calculation
    for query_term in query_terms_counts:
        weight_tq = calculate_tfidf_query(query_term, query_terms_counts[query_term], corpus_size)
        current_posting_list = get_postings_list(query_term)
        for doc_id in main_posting_list:
            if doc_id in current_posting_list:
                scores[doc_id] += weight_tq * calculate_tfidf_documents(query_term, current_posting_list[doc_id])

    # normalize lengths
    for doc_id, score in scores.items():
        scores[doc_id] = score / doc_id_len_pairs[doc_id]

    return scores


def curate_doc_scores(scores):

    #Returns the top 10 scoring documents using a max heap

    heap = [(-value, key) for key, value in scores.items()]
    largest = hq.nsmallest(len(scores), heap)
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
