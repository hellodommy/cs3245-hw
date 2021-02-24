#!/usr/bin/python3
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import *
import sys
import getopt
import string
import os

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    stemmer = PorterStemmer()
    punc = string.punctuation
    index = {}
    for entry in os.listdir(in_dir):
        full_path = os.path.join(in_dir, entry)
        if os.path.isfile(full_path) and not entry.startswith('.'):
            with open(full_path, 'r') as file:
                data = file.read().replace('\n', '') # string data for each document
                for sent in sent_tokenize(data):
                    for word in word_tokenize(sent):
                        if word not in punc:
                            case_fold = word.lower()
                            stemmed = stemmer.stem(case_fold)
                            if (stemmed not in index):
                                index[stemmed] = [int(entry)]
                            else:
                                curr_posting_list = index[stemmed]
                                if (int(entry) not in curr_posting_list):
                                    curr_posting_list.append(int(entry));
                                    index[stemmed] = curr_posting_list
    print(index)


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
