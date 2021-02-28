#!/usr/bin/python3
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import *
import sys
import getopt
import string
import os
import _pickle as pickle
import math

punc = string.punctuation
block_count = 0 # running count of the number of blocks
max_len = 0
BLOCKS = "blocks"

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
    os.makedirs(BLOCKS, exist_ok=True)
    limit = 5
    doc_list = os.listdir(in_dir)
    doc_chunks = [doc_list[i * limit:(i + 1) * limit] for i in range((len(doc_list) + limit - 1) // limit)]
    for chunk in doc_chunks:
        spimi_invert(chunk, in_dir)
    merge(BLOCKS)

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
    write_block_to_disk(index, output_file)

def write_block_to_disk(index, output_file):
    global max_len
    index_items = index.items()
    max_len = max(max_len, len(index_items))
    for key, value in index_items: # sorting each postings list
        value.sort()
    index_items = sorted(index_items) # sorting term
    output = open(os.path.join(BLOCKS, output_file), 'wb')
    for item in index_items:
        pickle.dump(item, output)
    output.close()
    
def merge(in_dir):
    global max_len
    limit = 5
    loops = math.ceil(max_len / limit)
    opened_files = {}
    removed_files = []
    # open all files and store in list
    for entry in os.listdir(in_dir):
        opened_files[entry] = open(os.path.join(in_dir, entry), 'rb')
    for i in range(loops):  # 1 reading of limit lines
        unpickled = []
        for key, value in opened_files.items():
            unpickler = pickle.Unpickler(value)
            for j in range(limit):
                if key not in removed_files:
                    try:
                        unpickled.append(unpickler.load())
                    except EOFError as error:
                        removed_files.append(key)
            # do the merge now
        unpickled.sort()
        # merge unpickled here
        merge_unpickled = []
        curr_term = ""
        for unpickle in unpickled:
            if unpickle[0] != curr_term:
                merge_unpickled.append(unpickle)
                curr_term = unpickle[0]
            else:
                last_index = len(merge_unpickled) - 1
                temp_list = merge_unpickled[last_index][1]
                temp_list.extend(unpickle[1])
                temp_list.sort()
                merge_unpickled[last_index] = [unpickle[0], temp_list]
        # write out merge unpickled
        #print(merge_unpickled)

        #print(unpickled)
        #print("__________\n")

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
