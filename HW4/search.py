#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import math
import functools
import time
import _pickle as pickle
from nltk import ngrams
from nltk.corpus import wordnet as wn
from data import set_postings_file, read_dict, get_corpus_size, get_doc_id_len_pairs, get_postings_list, get_doc_ids, get_doc_freq, get_main_posting_list

RELEVANT = {}

def get_rel_terms():
    '''
    Retrieves relevant terms for each document from indexing stage
    '''
    f = open('rel.txt', 'rb')
    unpickler = pickle.Unpickler(f)
    while True:
        try:
            entry = unpickler.load()
            doc_id = entry[0]
            terms = entry[1]
            RELEVANT[int(doc_id)] = terms
        except EOFError:
            break

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    '''
    Uses the given dictionary file and postings file
    to perform searching on the given queries file and
    output the results to a file
    '''
    start = time.perf_counter()
    print('running search on the queries...')
    set_postings_file(postings_file)
    read_dict(dict_file)  # read from dictionary file and store in memory

    rf = open(results_file, 'w+', encoding="utf-8")
    rf.write('')
    rf.close()

    queries = open(queries_file, 'r', encoding="utf-8")
    lines = queries.readlines()
    query = ''
    rel_docs = []
    for i in range(len(lines)):
        if i == 0:
            query = lines[i].rstrip()
        else:
            rel_docs.append(int(lines[i]))

    rf = open(results_file, 'a', encoding="utf-8")
    query_terms = parse_query(query)

    expand_query_terms = query_expand(query_terms)
    
    get_rel_terms()
    for rel_doc in rel_docs:
        try:
            # the important terms from each relevant doc are placed in one segment together
            expand_query_terms.append(RELEVANT[rel_doc])
        except KeyError: # doc is not found in relevant term dictionary
            continue
    
    query_terms_counts = counter(expand_query_terms)
    doc_scores = calculate_cosine_scores(expand_query_terms, query_terms_counts)
    result_docs = [k for k, v in sorted(doc_scores.items(), key=lambda item: (-item[1], item[0]))]

    for i in range(len(result_docs)):
        if i == len(result_docs) - 1:
            rf.write(str(result_docs[i]))
        else:
            rf.write(str(result_docs[i]) + ' ')

    rf.close()
    end = time.perf_counter()
    print(f"Completed in {end - start:0.4f} seconds")


def parse_query(query):
    '''
    Example - Query: 'what is "fertility treatment" AND damages'
    Output - [['what', 'is', 'fertility_treatment'], ['damages']]
    '''
    parsed_terms = []
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
                quote += segment[i].strip('"') + "_"
            elif segment[i].endswith('"'):
                is_quote = False
                quote += segment[i].strip('"')
                segment_terms.append(quote)
                quote = ""
            elif not is_quote:
                segment_terms.append(segment[i])
            else:
                quote += segment[i] + "_"
        parsed_terms.append(segment_terms)

    return parsed_terms


def generate_syn(prev_value, next_value):
    name = next_value.name()
    if name not in prev_value:
        prev_value.append(name)
    return prev_value


def query_expand(parsed_terms):
    expanded_query_terms = []
    for segment in parsed_terms:
        segment_terms = []
        for term in segment:
            for syn in wn.synsets(term):
                lemma_arr = syn.lemmas()
                segment_terms = functools.reduce(generate_syn, lemma_arr, segment_terms)
        segment_terms += segment  # concatenate original query terms
        expanded_query_terms.append(segment_terms)

    return expanded_query_terms


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


def calculate_tfidf_documents(zone):
    '''
    Calculates the tf-idf (lnc) for a document
    '''
    # title (0), content (1), date (2), court (3)
    alpha = [0.470588, 0.176471, 0.117647, 0.235294]
    result = 0
    for i in range(len(zone)):
        if zone[i] != 0:
            tf = 1 + math.log(zone[i], 10)
            result += alpha[i] * tf

    return result  # idf not calculated for documents


def add_to_count(term, dictionary):
    if term in dictionary:
        dictionary[term] += 1
    else:
        dictionary[term] = 1


def counter(query_terms):
    count_dict = {}
    for segment in query_terms:
        for term in segment:
            split_term = term.split('_')
            if len(split_term) == 3:
                for item in list(ngrams(split_term, 2)):
                    to_add = item[0] + '_' + item[1]
                    add_to_count(to_add, count_dict)
            else:
                add_to_count(term, count_dict)
    return count_dict


def calculate_cosine_scores(query_terms, query_terms_counts):
    '''
    Returns a `scores` dictionary where the keys are doc IDs and the values are the cosine scores
    '''
    corpus_size = get_corpus_size()
    doc_id_len_pairs = get_doc_id_len_pairs()

    # retrieve all documents that fulfils the boolean requirement of query
    main_posting_list = get_main_posting_list(query_terms)
    scores = dict(zip(main_posting_list, [0] * len(main_posting_list)))

    # calculation
    for query_term in query_terms_counts:
        weight_tq = calculate_tfidf_query(query_term, query_terms_counts[query_term], corpus_size)
        current_posting_list = get_postings_list(query_term)
        for doc_id in main_posting_list:
            if doc_id in current_posting_list:
                scores[doc_id] += weight_tq * calculate_tfidf_documents(current_posting_list[doc_id])

    # normalize lengths
    for doc_id, score in scores.items():
        print(doc_id_len_pairs[doc_id])
        print(score)
        scores[doc_id] = score / doc_id_len_pairs[doc_id]

    return scores


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
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
