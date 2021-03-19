from utility import tokenize

DICTIONARY = {}
DOC_ID_LEN_PAIRS = []
POSTINGS_FILE = ''

def get_doc_ids():
    global DOC_ID_LEN_PAIRS
    return list(map(lambda pair: pair[0], DOC_ID_LEN_PAIRS))

def get_doc_lengths():
    global DOC_ID_LEN_PAIRS
    return list(map(lambda pair: pair[1], DOC_ID_LEN_PAIRS))

def get_doc_id_len_pairs():
    global DOC_ID_LEN_PAIRS
    return DOC_ID_LEN_PAIRS

def set_postings_file(postings_file):
    global POSTINGS_FILE
    POSTINGS_FILE = postings_file

def read_posting(byte_offset, bytes_to_read):
    '''
    Read specified bytes from the posting list at a byte offset
    '''
    f = open(POSTINGS_FILE, 'r')
    result = ''
    f.seek(byte_offset)
    result += f.read(bytes_to_read)
    f.close()
    return result

def read_dict(dict_file):
    '''
    Reads a dictionary from disk into memory
    '''
    global DICTIONARY, DOC_ID_LEN_PAIRS
    f = open(dict_file, 'r')
    for line in f.readlines():
        info = (line.rstrip()).split(' ')
        if info[0] == '*': # encountered special term for all our doc ids
            doc_ids_w_length = read_posting(int(info[2]), int(info[3])).split(' ')
            for id_len_str_pair in doc_ids_w_length:
                id_len_str_split = id_len_str_pair.split('-')
                DOC_ID_LEN_PAIRS.append((int(id_len_str_split[0]), int(id_len_str_split[1])))
            continue
        # term: [doc_freq, absolute_offset, accumulative_offset]
        DICTIONARY[info[0]] = [int(info[1]), int(info[2]), int(info[3])]
    assert '*' not in DICTIONARY
    f.close()
 
def get_doc_freq(term):
    '''
    Returns document frequency for the term
    '''
    try:
        return DICTIONARY[tokenize(term)][0]
    except KeyError as error:
        return 0

def get_postings_list(term):
    '''
    Returns postings list for the term
    '''
    try:
        dict_info = DICTIONARY[tokenize(term)]
        posting = read_posting(dict_info[1], dict_info[2])
        postings_list = []
        for id_len_str_pair in posting.split(' '):
            id_len_str_split = id_len_str_pair.split('-')
            postings_list.append((int(id_len_str_split[0]), int(id_len_str_split[1])))
        return postings_list
    except KeyError as error:
        return []

def get_corpus_size():
    '''
    Returns the size of the entire corpus
    '''
    return len(DOC_ID_LEN_PAIRS)