# script to check if dictionary was written out to pickle correctly

import _pickle as pickle

file = pickle.load(open("blocks/block11.txt", "rb"))
print(file)
