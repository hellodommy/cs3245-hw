This is the README file for A0189690L and A0000000X's submission

== Python Version ==

We're using Python Version <3.7.6 or replace version number> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Tokenisation:
We are using the following:
- Ignoring punctuation based on str.punctuation
- Case folding on all words
- Porter stemming

Index Construction Method:
For indexing, we are using SPIMI because of the efficiency it has over BSBI.
For each call of SPIMI Invert, we feed it a chunk of documents.
We have currently set the limit to 5 as articles can be long,
but the limit is a variable can easily be changed.
Every 5 document chunks will be written to a block.
Then, an n-way merge is performed,
where we read a limit number of lines from each block into memory,
so the efficiency is not lost by disk seeks.
Like before, this limit is also set to 5
and can be easily changed.

Skip Pointers:
Before the posting list is written to disk,
we add skip pointers to the posting list for every sqrt(n) postings.

Search Method:
We use the Shunting Yard algorithm to convert infix queries to postfix.
These postfix queries are continually evaluted until we are left
with the final result.

Optimisation:
1. We have made use of skip pointers in intersection AND queries
to make for faster merge.
2. We have added skip pointers to intermediate results also to
facilitate faster merged.
3. NOT queries are "postponed" until we can get an intersection
with another query to avoid going through the whole corpus.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py - indexes corpus into dictionary and postings file
search.py - conducts search on the indexed corpus
utility.py - contains utility methods used by index.py and search.py

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0189690L and A0000000X, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

Handling files in Python
https://realpython.com/working-with-files-in-python/

Reading file line by line into list
https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list#comment44278184_3277516

Read list in chunks
https://geeksforgeeks.org/break-list-chunks-size-n-python/

Using a global variable in Python
https://vbsreddy1.medium.com/unboundlocalerror-when-the-variable-has-a-value-in-python-e34e097547d6

Convert query infix to postifx
https://en.wikipedia.org/wiki/Shunting-yard_algorithm