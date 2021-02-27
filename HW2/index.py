#!/usr/bin/python3
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import *
import sys
import getopt
import string
import os
import _pickle as pickle

punc = string.punctuation
block_count = 0

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
    os.makedirs('blocks', exist_ok=True)
    limit = 5
    doc_list = os.listdir(in_dir)
    doc_chunks = [doc_list[i * limit:(i + 1) * limit] for i in range((len(doc_list) + limit - 1) // limit)]
    for chunk in doc_chunks:
        spimi_invert(chunk, in_dir)

def tokenize(word):
    stemmer = PorterStemmer()
    word = word.lower()
    word = stemmer.stem(word)
    return word

def spimi_invert(chunk, in_dir):
    global block_count
    block_count += 1
    output_file = "block" + str(block_count) + ".txt"
    index = {}
    for entry in chunk:
        full_path = os.path.join(in_dir, entry)
        if os.path.isfile(full_path):
            file = open(full_path, "r")
            doc = file.read().replace('\n', '')
            for sent in sent_tokenize(doc):
                for word in word_tokenize(sent):
                    if word not in punc:
                        tokenized = tokenize(word)
                        if (tokenized not in index):
                                index[tokenized] = [int(entry)]
                        else:
                            curr_posting_list = index[tokenized]
                            if (int(entry) not in curr_posting_list):
                                curr_posting_list.append(int(entry))
                                index[tokenized] = curr_posting_list
            file.close()
    for item in index:
        index[item].sort()
    index_items = index.items()
    index_items = sorted(index_items)
    output = open(os.path.join('blocks', output_file), 'wb')
    output.write(pickle.dumps(index_items))
    output.close()

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
