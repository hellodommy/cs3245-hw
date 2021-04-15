#!/usr/bin/python3
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import bigrams
import sys
import getopt
import string
import os
import csv
import _pickle as pickle
import math
from queue import PriorityQueue
from utility import tokenize

punc = string.punctuation
block_count = 0  # running count of the number of blocks
max_len = 0
BLOCKS = "blocks"
DICTIONARY = {}  # stores (key, value) as (doc_id, doc_len)

def usage():
    print("usage: " +
          sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    '''
    Builds index from documents stored in the input directory,
    then output the dictionary file and postings file
    '''
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    csv.field_size_limit(sys.maxsize)
    limit = 20
    os.makedirs(BLOCKS, exist_ok=True)

    with open(in_dir) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        doc_list = list(csv_reader)
        doc_list = doc_list[1:] # ignore header line
        doc_chunks = [doc_list[i * limit:(i + 1) * limit]
                    for i in range((len(doc_list) + limit - 1) // limit)]
        for chunk in doc_chunks:
            spimi_invert(chunk, in_dir)
    f = open(out_dict, 'w+')
    f.close()
    f = open(out_postings, 'w+')
    f.close()
    offset = record_doc_length(out_dict, out_postings)
    merge(BLOCKS, out_dict, out_postings, offset)

def record_doc_length(out_dict, out_postings):
    '''
    Records docIDs and their respective normalised doc lengths
    '''
    global DICTIONARY
    result = ''

    for doc_id, doc_len in sorted(DICTIONARY.items()):
        result += str(doc_id) + '-' + str(doc_len) + ' '

    # (doc_frequency, absolute_offset, accumulative_offset)
    dict_expr = "* 0 0 " + str(len(result)) + "\n"

    write_to_file(out_dict, dict_expr)
    write_to_file(out_postings, result)

    return len(result)

def write_to_file(file, content):
    '''
    Writes out lines to disk for search phase later
    '''
    fw = open(file, 'a')
    fw.write(''.join(content))
    fw.close()

def spimi_invert(chunk, in_dir):
    '''
    Executes SPIMI Invert algorithm for each chunk of documents
    For each chunk, store a master index
    For each entry in the chunk, collect term frequencies and calculate the weights (for normalised doc length)
    Add [doc id, term freq] to the master index and log the normalised document length
    '''
    global block_count, DICTIONARY
    print('block:', block_count)
    index = {} # index for the whole chunk
    for entry in chunk:
        entry_index = {}
        doc_id, title, content, date, court = entry[0], entry[1], entry[2], entry[3], entry[4]
        title_words = []
        for word in word_tokenize(title.rstrip()):  # title
            if word not in punc:
                    tokenized = tokenize(word)
                    title_words.append(tokenized)
                    if (tokenized not in entry_index):
                        zones = set()
                        zones.add('b')  # add title zone
                        entry_index[tokenized] = [int(doc_id), 1, zones]
                    else:
                        curr_count = entry_index[tokenized][1]
                        zones = entry_index[tokenized][2]
                        zones.add('b')
                        entry_index[tokenized] = [
                            int(doc_id), curr_count + 1, zones]
        for entry in list(bigrams(title_words)):  # title bigrams
            bigram = entry[0] + "-" + entry[1]
            if (bigram not in entry_index):
                zones = set()
                zones.add('b')  # add title zone
                entry_index[bigram] = [int(doc_id), 1, zones]
            else:
                curr_count = entry_index[bigram][1]
                zones = entry_index[bigram][2]
                zones.add('b')
                entry_index[bigram] = [int(doc_id), curr_count + 1, zones]
        content_words = []
        for sent in sent_tokenize(content): # content
            for word in word_tokenize(sent):
                 if word not in punc:
                        tokenized = tokenize(word)
                        content_words.append(tokenized)
                        if (tokenized not in entry_index):
                            zones = set()
                            zones.add('c') # add content zone
                            entry_index[tokenized] = [int(doc_id), 1, zones]
                        else:
                            curr_count = entry_index[tokenized][1]
                            zones = entry_index[tokenized][2]
                            zones.add('c')
                            entry_index[tokenized] = [int(doc_id), curr_count + 1, zones]
        for entry in list(bigrams(content_words)):  # content bigrams
            bigram = entry[0] + "-" + entry[1]
            if (bigram not in entry_index):
                zones = set()
                zones.add('c')  # add content zone
                entry_index[bigram] = [int(doc_id), 1, zones]
            else:
                curr_count = entry_index[bigram][1]
                zones = entry_index[bigram][2]
                zones.add('c')
                entry_index[bigram] = [int(doc_id), curr_count + 1, zones]
        for word in word_tokenize(date.rstrip()):  # date
            if word not in punc:
                    tokenized = tokenize(word)
                    if (tokenized not in entry_index):
                        zones = set()
                        zones.add('d')  # add date zone
                        entry_index[tokenized] = [int(doc_id), 1, zones]
                    else:
                        curr_count = entry_index[tokenized][1]
                        zones = entry_index[tokenized][2]
                        zones.add('d')
                        entry_index[tokenized] = [ int(doc_id), curr_count + 1, zones]
        court_words = []
        for word in word_tokenize(court.rstrip()):  # court
            if word not in punc:
                tokenized = tokenize(word)
                court_words.append(tokenized)
                if (tokenized not in entry_index):
                    zones = set()
                    zones.add('e')  # add content zone
                    entry_index[tokenized] = [int(doc_id), 1, zones]
                else:
                    curr_count = entry_index[tokenized][1]
                    zones = entry_index[tokenized][2]
                    zones.add('e')
                    entry_index[tokenized] = [
                        int(doc_id), curr_count + 1, zones]
        for entry in list(bigrams(court_words)):  # court bigrams
            bigram = entry[0] + "-" + entry[1]
            if (bigram not in entry_index):
                zones = set()
                zones.add('e')  # add content zone
                entry_index[bigram] = [int(doc_id), 1, zones]
            else:
                curr_count = entry_index[bigram][1]
                zones = entry_index[bigram][2]
                zones.add('e')
                entry_index[bigram] = [int(doc_id), curr_count + 1, zones]
        doc_len = 0
        for token, posting_list in entry_index.items():
            doc_len += (1 + math.log10(posting_list[1]))**2
            if token not in index:
                index[token] = [posting_list]
            else:
                curr_posting = index[token]
                curr_posting.append(posting_list)
                index[token] = curr_posting
        DICTIONARY[int(doc_id)] = math.sqrt(doc_len)
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
    for key, value in index_items:  # sorting each postings list
        value.sort() # sort by doc_id
    index_items = sorted(index_items) # sort terms
    output = open(os.path.join(BLOCKS, output_file), 'wb')
    for item in index_items:
        pickle.dump(item, output)
    output.close()


def merge(in_dir, out_dict, out_postings, offset):
    '''
    Performs n-way merge, reading limit-number of entries from each block at a time
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
            posting_list_str = posting_to_str(posting_list_to_write)

            # (doc_frequency, absolute_offset, accumulative_offset)
            dict_entry = term_to_write + " " + str(len(posting_list_to_write)) + " " + str(
                offset) + " " + str(len(posting_list_str)) + "\n"
            write_to_file(out_dict, dict_entry)
            write_to_file(out_postings, posting_list_str)

            offset += len(posting_list_str)

            # resetting variables for new term
            term_to_write = term
            posting_list_to_write = posting_list
        else:  # curr_term == term
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


def posting_to_str(posting_list):
    '''
    Converts a posting list to string form of docID-termFreq-zones
    '''
    result = ''
    for posting in posting_list:
        zones = ""
        zones = zones.join(posting[2])
        result += str(posting[0]) + '-' + str(posting[1]) + '-' + zones + ' '
    return result

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
