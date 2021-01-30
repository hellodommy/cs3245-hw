#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt

from nltk import ngrams

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    # This is an empty method
    # Pls implement your code below


    malay_dict = {}
    indo_dict = {}
    tamil_dict = {}

    malay_count = 0
    indo_count = 0
    tamil_count = 0

    f = open(in_file, 'r')

    lines = f.readlines()

    for line in lines:
        lang = line.split(' ', 1)[0].strip()
        sentence = line.split(' ', 1)[1].rstrip()
        tokens = list(ngrams(sentence, 4))
        for token in tokens:
            if lang == 'tamil':
                count = tamil_dict.get(token, 0)
                new_count = count + 1
                tamil_dict[token] = new_count
                tamil_count += 1
            if lang == 'malaysian':
                count = malay_dict.get(token, 0)
                new_count = count + 1
                malay_dict[token] = new_count
                malay_count += 1
            if lang == 'indonesian':
                count = indo_dict.get(token, 0)
                new_count = count + 1
                indo_dict[token] = new_count
                indo_count += 1

    malay_dict, indo_dict, tamil_dict, malay_count, indo_count, tamil_count = smoothing(malay_dict, indo_dict, tamil_dict, malay_count, indo_count, tamil_count)
    
    print("malay dict:", malay_dict)
    print("malay count:", malay_count)
    print("indo dict:", indo_dict)
    print("indo count:", indo_count)
    print("tamil dict:", tamil_dict)
    print("tamil count:", tamil_count)


def smoothing(malay_dict, indo_dict, tamil_dict, malay_count, indo_count, tamil_count):
    # Add one to existing
    for key in tamil_dict:
        count = tamil_dict.get(key)
        new_count = count + 1
        tamil_dict[key] = new_count
        tamil_count += 1
    for key in malay_dict:
        count = malay_dict.get(key)
        new_count = count + 1
        malay_dict[key] = new_count
        malay_count += 1
    for key in indo_dict:
        count = indo_dict.get(key)
        new_count = count + 1
        indo_dict[key] = new_count
        indo_count += 1
    # Add ones not existing
    for key in tamil_dict:
        if key not in malay_dict:
            malay_dict[key] = 1
            malay_count += 1
        if key not in indo_dict:
            indo_dict[key] = 1
            indo_count += 1
    for key in malay_dict:
        if key not in tamil_dict:
            tamil_dict[key] = 1
            tamil_count += 1
        if key not in indo_dict:
            indo_dict[key] = 1
            indo_count += 1
    for key in indo_dict:
        if key not in malay_dict:
            malay_dict[key] = 1
            malay_count += 1
        if key not in tamil_dict:
            tamil_dict[key] = 1
            tamil_count += 1

    return malay_dict, indo_dict, tamil_dict, malay_count, indo_count, tamil_count
    
def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code below


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
