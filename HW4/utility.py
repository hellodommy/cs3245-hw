from nltk.stem.porter import *
import string
import re

punc = string.punctuation


def is_valid(word):
    '''
    Checks if a word is valid (not punctuation and not foriegn character)
    '''
    return word not in punc and not cjk_detect(word)


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

# Taken from https://medium.com/the-artificial-impostor/detecting-chinese-characters-in-unicode-strings-4ac839ba313a
def cjk_detect(texts):
    '''
    Detect Chinese, Japanese and Korean words
    '''
    # korean
    if re.search("[\uac00-\ud7a3]", texts):
        return True
    # japanese
    if re.search("[\u3040-\u30ff]", texts):
        return True
    # chinese
    if re.search("[\u4e00-\u9FFF]", texts):
        return True
    return False
