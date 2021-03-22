from nltk.stem.porter import *

def tokenize(word):
    '''
    Tokenises a given word with Porter Stemmer and case folding
    '''
    word = word.lower()
    word = PorterStemmer().stem(word)
    return word
