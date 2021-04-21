from nltk.stem.porter import *
from nltk.corpus import stopwords
import string
import re

punc = string.punctuation
stop_words = set(stopwords.words('english'))


def is_valid(word):
    '''
    Checks if a word is valid (not punctuation and not foriegn character and not stopword)
    '''
    return (word not in punc) and not is_cjk(word) and (word not in stop_words)


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
def is_cjk(texts):
    '''
    Checks for Chinese, Japanese and Korean words
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
