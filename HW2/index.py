#!/usr/bin/python3
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import sys
import getopt
import string
import os
import _pickle as pickle
import math
from queue import PriorityQueue
from utility import tokenize, add_skip_ptr

punc = string.punctuation
block_count = 0 # running count of the number of blocks
max_len = 0
DOC_IDS = []
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
    
    limit = 20
    doc_list = os.listdir(in_dir)
    doc_chunks = [doc_list[i * limit:(i + 1) * limit] for i in range((len(doc_list) + limit - 1) // limit)]
    for chunk in doc_chunks:
        spimi_invert(chunk, in_dir)
    
    f = open(out_dict, 'w+')
    f.close()
    f = open(out_postings, 'w+')
    f.close()

    offset = log_doc_ids(out_dict, out_postings)
    merge(BLOCKS, out_dict, out_postings, offset)

def log_doc_ids(out_dict, out_postings):
    '''
    Collecting all docIDs to support NOT queries in search phase
    '''
    global DOC_IDS
    DOC_IDS.sort()

    str_form = ''
    for doc_id in DOC_IDS:
        str_form += str(doc_id) + ' '
    
    # (doc_frequency, absolute_offset, accumulative_offset)
    dict_expr = "* 0 0 " + str(len(str_form)) + "\n"
    
    write_to_file(out_dict, dict_expr)
    write_to_file(out_postings, str_form)
    
    return len(str_form)

def spimi_invert(chunk, in_dir):
    '''
    Executes SPIMI Invert algorithm for each chunk of documents
    '''
    global block_count, DOC_IDS

    index = {}
    for entry in chunk:
        DOC_IDS.append(int(entry))
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
    
    block_count += 1
    output_file = "block" + str(block_count) + ".txt"
    write_block_to_disk(index, output_file)

def write_block_to_disk(index, output_file):
    '''
    Writes out a block to disk in /blocks folder
    '''
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

def merge(in_dir, out_dict, out_postings, offset):
    '''
    Perform n-way merge, reading limit-number of entries from each block at a time
    '''
    global max_len
    limit = 5
    loops = math.ceil(max_len / limit)
    opened_files = {}
    removed_files = []

    # open all files and store in list
    for entry in os.listdir(in_dir):
        opened_files[entry] = open(os.path.join(in_dir, entry), 'rb')
    
    # initialising PQ
    pq = PriorityQueue()
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
    while not pq.empty():
        item = pq.get()
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
        
        if block_name not in removed_files:
            try:
                unpickler = pickle.Unpickler(opened_files[block_name])
                temp_item = list(unpickler.load())
                # block where the item of (term, docID) is from
                temp_item.append(block_name)
                pq.put(temp_item)
            except EOFError as error:
                removed_files.append(block_name)

def write_to_file(file, content):
    '''
    Writes out lines to disk for search phase later
    '''
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
