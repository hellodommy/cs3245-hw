# script to check if dictionary was written out to pickle correctly

import _pickle as pickle

favorite_color = pickle.load(open("block2.txt", "rb"))
print(type(favorite_color))