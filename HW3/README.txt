This is the README file for A0189690L and A0190198W's submission
We are contactable at e0325274@u.nus.edu and e0325782@u.nus.edu respectively.

== Python Version ==

We're using Python Version 3.7.3 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Our program indexes the corpus using SPIMI as before in HW2.
Some modifications were made to keep the term frequency along with the docID
in the posting list,
and to keep the weighted tf of terms to get the normalised doc length.

Searching is done using the cosinescore algorithm from Lecture 7, Slide 38.
tf-idf is calculated for query and documents,
then the score is added to a scores dictionary.
A max heap of size 10 is used to get the top 10 documents from the scores dictionary,
so that the large scores dictionary does not have to be sorted.

Writing to the result is stopped once we encounter a score of 0
which means that the current document and subsequent ones are
not a match and should not be included in the result.

This ensures that all docIDs within the top 10 are a match.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py - Indexes the corpus using SPIMI
search.py - Searches the corpus usiing ranked retrieval
data.py - Contains methods that access the dictionary and the respective posting list
utility.py - Contains utility function shared by other modules (tokenizer)

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0189690L and A0190198W, certify that we have followed the CS 3245 Information
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

- Implementation of max heap, sorted by value: https://stackoverflow.com/questions/14795333/how-to-maintain-dictionary-in-a-heap-in-python/14795642#14795642