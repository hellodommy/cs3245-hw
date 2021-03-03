from nltk.stem.porter import *
import math

def tokenize(word):
    stemmer = PorterStemmer()
    word = word.lower()
    word = stemmer.stem(word)
    return word

def add_skip_ptr(posting_list):
    '''
    Returns a string form of posting list with skip pointers, indicated by carat
    '''
    l = len(posting_list)
    result = ''
    if l > 2:
        num_ptr = math.floor(math.sqrt(l))
        ptr_gap = math.floor(l / num_ptr)
        for i in range(l):
            if i % ptr_gap == 0 and i < l - 2:
                if i + ptr_gap >= l:
                    result += str(posting_list[i]) + \
                        ' ^' + str(l - i - 1) + ' '
                else:
                    result += str(posting_list[i]) + ' ^' + str(ptr_gap) + ' '
            else:
                result += str(posting_list[i]) + ' '
    else:
        for i in range(l):
            result += str(posting_list[i]) + ' '
    return result
