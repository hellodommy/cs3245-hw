from utility import tokenize

DICTIONARY = {}
DOC_ID_LEN_PAIRS = {}
POSTINGS_FILE = ''

def get_doc_ids():
    global DOC_ID_LEN_PAIRS
    return DOC_ID_LEN_PAIRS.keys()

def get_doc_lengths():
    global DOC_ID_LEN_PAIRS
    return DOC_ID_LEN_PAIRS.values()

def get_doc_id_len_pairs():
    global DOC_ID_LEN_PAIRS
    return DOC_ID_LEN_PAIRS

def set_postings_file(postings_file):
    global POSTINGS_FILE
    POSTINGS_FILE = postings_file

def read_posting(byte_offset, bytes_to_read):
    '''
    Reads specified bytes from the posting list at a byte offset
    '''
    f = open(POSTINGS_FILE, 'r', encoding="utf-8")
    result = ''
    f.seek(byte_offset)
    result += f.read(bytes_to_read)
    f.close()
    return result

def read_dict(dict_file):
    '''
    Reads dictionary from disk into memory
    '''
    global DICTIONARY, DOC_ID_LEN_PAIRS
    f = open(dict_file, 'r', encoding="utf-8")
    for line in f.readlines():
        info = (line.rstrip()).split(' ')
        if info[0] == '*': # encountered special term for all our doc ids
            doc_ids_w_length = read_posting(int(info[2]), int(info[3])).rstrip().split(' ')
            for id_len_str_pair in doc_ids_w_length:
                id_len_str_split = id_len_str_pair.split('-')
                DOC_ID_LEN_PAIRS[int(id_len_str_split[0])] = float(id_len_str_split[1])
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

def or_op(pl_1, pl_2):
    if len(pl_1) == 0:
        return pl_2
    elif len(pl_2) == 0:
        return pl_1
    else:
        result = pl_1
        for doc_id in pl_2:
            if doc_id not in result:
                 result.append(doc_id)
        result.sort()
        return result


def and_op(pl_1, pl_2):
    result = []
    len1 = len(pl_1)
    len2 = len(pl_2)
    track1 = 0
    track2 = 0
    while track1 < len1 and track2 < len2:
        if pl_1[track1] == pl_2[track2]:
            result.append(pl_1[track1])
            track1 += 1
            track2 += 1
        elif pl_1[track1] < pl_2[track2]:
            track1 += 1
        else:
            track2 += 1

    return result

def get_postings_list(query_term):
    #[[ha, ha, ha, This is cold], [This is hot]]
    '''
    Returns postings list for the term (as a dictionary)
    '''
    try:
        dict_info = DICTIONARY[tokenize(query_term)]
        posting = read_posting(dict_info[1], dict_info[2]).rstrip()
        postings_list = {}
        doc_id_gap_accum = 0
        for gap_len_str_pair in posting.split(' '):
            gap_len_str_split = gap_len_str_pair.split('-')
            zones = gap_len_str_split[1].split(',')
            for i in range(len(zones)):
                if zones[i] == '':
                    zones[i] = 0
                else:
                    zones[i] = int(zones[i])
            doc_id = doc_id_gap_accum + int(gap_len_str_split[0])
            doc_id_gap_accum += doc_id
            postings_list[doc_id] = zones
        return postings_list
    except KeyError as error:
        return {}

def get_intermediate_postings(query_term):
    '''
    Returns doc_ids for the term (as an array)
    '''
    try:
        dict_info = DICTIONARY[tokenize(query_term)]
        posting = read_posting(dict_info[1], dict_info[2]).rstrip()
        postings_list = []
        doc_id_gap_accum = 0
        for gap_len_str_pair in posting.split(' '):
            gap_len_str_split = gap_len_str_pair.split('-')
            doc_id = doc_id_gap_accum + int(gap_len_str_split[0])
            doc_id_gap_accum += doc_id
            postings_list.append(doc_id)
        return postings_list
    except KeyError as error:
        return []

def get_main_posting_list(query_terms):
    main_posting_list = []
    #[[ha, ah, ha2, This is cold], [This is hot]]
    for segment in query_terms:
        #[ha, ah, ha2, This is cold]
        intermediate_posting_list = []
        for term in segment:
            split_term = term.split('_')
            if len(split_term) == 3:
                biword_1 = split_term[0] + "_" + split_term[1]
                biword_2 = split_term[1] + "_" + split_term[2]
                temp = and_op(get_intermediate_postings(biword_1), get_intermediate_postings(biword_2))
                intermediate_posting_list = or_op(intermediate_posting_list, temp)
            else:
                intermediate_posting_list = or_op(intermediate_posting_list, get_intermediate_postings(term))


        if len(main_posting_list) == 0:
            main_posting_list = intermediate_posting_list
        else:
            main_posting_list = and_op(main_posting_list, intermediate_posting_list)

    return main_posting_list

def get_corpus_size():
    '''
    Returns the size of the entire corpus
    '''
    return len(DOC_ID_LEN_PAIRS)
