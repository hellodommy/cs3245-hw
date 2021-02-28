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
from queue import PriorityQueue

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
    f = open(out_dict, 'w+')
    f.close()
    f = open(out_postings, 'w+')
    f.close()
    merge(BLOCKS, out_dict, out_postings)

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

def merge(in_dir, out_dict, out_postings):
    global max_len
    limit = 5
    loops = math.ceil(max_len / limit)
    opened_files = {}
    removed_files = []
    # open all files and store in list
    for entry in os.listdir(in_dir):
        opened_files[entry] = open(os.path.join(in_dir, entry), 'rb')
    pq = PriorityQueue()
    # initialising PQ
    for i in range(limit):
        for block_name, file_read in opened_files.items():
            unpickler = pickle.Unpickler(file_read)
            if block_name not in removed_files:
                try:
                    temp_item = list(unpickler.load())
                    # block where the item of (term, docID) is from
                    temp_item.append(block_name)
                    pq.put(temp_item)
                except EOFError as error:
                    removed_files.append(block_name)
    term_to_write = ''
    posting_list_to_write = []
    offset = 0
    while not pq.empty():
        item = pq.get()
        #print(item)
        term, posting_list, block_name = item[0], item[1], item[2]
        if term_to_write == '':  # first term we are processing
            term_to_write = term
            posting_list_to_write = posting_list
        elif term_to_write != term:  # time to write our current term to to disk because we encountered a new term
            posting_list_to_write.sort()
            posting_list_w_skip_ptr = add_skip_ptr(posting_list_to_write)
            # (doc_frequency, absolute_offset, accumulative_offset)
            dict_entry = term_to_write + " " + str(len(posting_list_to_write)) + " " + str(offset) + " " + str(len(posting_list_w_skip_ptr)) + "\n"
            write_to_file(out_dict, dict_entry)
            write_to_file(out_postings, posting_list_w_skip_ptr)
            offset += len(posting_list_w_skip_ptr)
            term_to_write = term
            posting_list_to_write = posting_list
        else: # curr_term == term
            posting_list_to_write.extend(posting_list)

        # do we need to check if block is in removed files
        if block_name not in removed_files:
            try:
                unpickler = pickle.Unpickler(opened_files[block_name])
                temp_item = list(unpickler.load())
                # block where the item of (term, docID) is from
                temp_item.append(block_name)
                pq.put(temp_item)
            except EOFError as error:
                removed_files.append(block_name)

def add_skip_ptr(posting_list):
    l = len(posting_list)
    result = ''
    if l > 2:
        num_ptr = math.floor(math.sqrt(l))
        ptr_gap = math.floor(l / num_ptr)
        for i in range(l):
            if i % ptr_gap == 0 and i < l - 2:
                if i + ptr_gap >= l:
                    result += str(posting_list[i]) + ' ^' + str(l - i - 1) + ' '
                else:
                    result += str(posting_list[i]) + ' ^' + str(ptr_gap) + ' '
            else:
                result += str(posting_list[i]) + ' '
    else:
        for i in range(l):
            result += str(posting_list[i]) + ' '
    return result

def write_to_file(file, content):
    fw = open(file, 'a')
    fw.write(''.join(content))
    fw.close()

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
