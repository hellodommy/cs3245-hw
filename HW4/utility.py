from nltk.stem.porter import *
from nltk.corpus import stopwords
import string
import re

stop_words = set(stopwords.words('english'))
valid_set = string.ascii_letters + string.digits


def is_valid(str):
    if str in stop_words:
        return False
    for letter in str:
        if letter not in valid_set:
            return False
    return True


def tokenize(word):
    '''
    Tokenises a given word with Porter Stemmer and case folding
    '''
    if "_" in word:  # encountering a biword
        first, second = word.split('_')[0], word.split('_')[1]
        return tokenize(first) + "_" + tokenize(second)
    else:
        word = word.lower()
        word = PorterStemmer().stem(word)
        return word

