from utility import tokenize

DICTIONARY = {}
DOC_IDS = ''
POSTINGS_FILE = ''

def get_doc_ids():
    global DOC_IDS
    return DOC_IDS

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
    global DICTIONARY, DOC_IDS
    f = open(dict_file, 'r')
    for line in f.readlines():
        info = (line.rstrip()).split(' ')
        if info[0] == '*': # encountered special term for all our doc ids
            DOC_IDS = read_posting(int(info[2]), int(info[3]))
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

def get_corpus_size():
    '''
    Returns the size of the entire corpus
    '''
    return len(DOC_IDS.rstrip().split(' '))

def separate_posting_and_skip(posting_list):
    '''
    Returns 2 lists
    1. Regular posting list
    2. Skip list
    '''
    skip_list = []
    reg_list = []
    posting_count = 0

    items = posting_list.rstrip().split(' ')
    item_count = 0
    try:
        while (item_count < len(items)):
            reg_list.append(int(items[item_count]))
            if item_count < len(items) - 1 and (items[item_count + 1][0] == '^'):
                skip_dist = int(items[item_count + 1][1:])
                skip_list.append(posting_count + skip_dist)
                item_count += 2  # move past the skip ptr
                posting_count += 1
            else:
                # there is no skip ptr assigned to this element
                skip_list.append(None)
                item_count += 1
                posting_count += 1
        assert len(reg_list) == len(skip_list)
    except ValueError as error:
        # posting_list string is empty
        return reg_list, skip_list

    return reg_list, skip_list

def get_posting_and_skip(op):
    '''
    Checks if item is an operand or an intermediate result and gets necesary posting list and skip list
    '''
    if op[0] == 'operand':
        tok = tokenize(op[1])
        try:
            offset, bytes_to_read = DICTIONARY[tok][1], DICTIONARY[tok][2]
            # getting posting list with skip ptr from postings file
            full_posting = read_posting(offset, bytes_to_read)
            return separate_posting_and_skip(full_posting)
        except KeyError as error:
            # token cannot be found in our dictionary
            return [], []
    else: # type is not or res
        try:
            return separate_posting_and_skip(op[1])
        except ValueError as error:
            # if intermediate result is blank
            return [], []
