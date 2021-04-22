This is the README file for A0189690L-A0190198W-A0199786X-A0200679A submission
Email for A0189690L: e0325274@u.nus.edu
Email for A0190198W: e0325782@u.nus.edu
Email for A0199786X: e0406767@u.nus.edu
Email for A0200679A: e0407660@u.nus.edu

== Python Version ==

We're using Python Version 3.8.5 for this assignment.

== General Notes about this assignment ==

Indexing
In build_index(), the data set is parsed and processed using the Single-Pass In-Memory Indexing (SPIMI) algorithm.
In spimi_invert(), a master index is created and as we process the data sets, we accumulate the term frequencies for the various zones for each document (to support weighted scoring based on zones in search). To support phrasal queries, we have also indexed the bigrams, in addition to unigrams, from the documents using the gen_unigram() and gen_bigram() functions.
In spimi_invert(), we also accumulate the normalised document lengths (to support the calculation of cosine scores in search).
We then add the [doc_id, zone_tfs] entries and the normalised document lengths to the master index before writing it to the disk using the write_block_to_disk() function.
Next, in the record_doc_length() function, we add the accumulative offsets (to indicate the length of the posting to read with reference to the previous posting) to the dictionary.
Finally, in merge(), we do a n-way merge of all the blocks to obtain the final dictionary and postings.

The dictionary has the format: “<term> <document frequency> <accumulative offset>”
The postings has the format: (For each term) “<doc_id> - <tf_title, tf_content, tf_date, tf_court>”
* The postings start with a list of “<doc_id gap> - <normalised_doc_length>”, followed by the posting lists which contains (for each term) the doc_ids and the respective zone tfs (format as shown above) 

Note for index.py:
The zone information is stored in the postings in order to save space. If this information is to be stored in the dictionary, the size of the dictionary will expand a few times, because each term when extracted from different zones, will be indexed as separate terms. On the other hand, storing in the postings will merely extend each [doc_id, zone_tfs] entry by a few bytes, making this the more logical choice. Moreover, for us to process the weight of the documents (in search) based on zones, it is much more efficient if the zone information is available in the same [doc_id, zone_tfs] entry in the same posting list, rather than having to look up several different posting lists just to obtain the information of all the zones (if the zone information is stored in the dictionary instead).
To support phrasal queries, we have decided to use bi-word indexing instead of positional indexing. Since we have already expanded the size of the postings (by storing additional zone information), we do not want to expand it further by storing positional information as well, hence, storing bi-word information in the dictionary is a justifiable choice. Furthermore, the space required to store positional index is way larger than that to store bi-word index, especially given the large data set that we have to index. Moreover, the search process is much simpler and more efficient using bi-word search as compared to positional search. Although there is the risk of getting false positives using bi-word search, we feel that it is a reasonable trade-off since we only have to support a maximum of three words in a phrasal query i.e. the effect of false positives is not as pronounced.
SPIMI algorithm is used for indexing because the data set that we have to index is large and there may not be enough storage in memory to process both the postings and dictionary simultaneously.

After performing indexing on the whole corpus, we realised that our files were too large - our dictionary.txt was 184MB (acceptable) but our postings.txt was 1.5GB. To meet the 700MB limit for submissions, we had to adopt some form of compression to minimise the size of our index.

Since the issue was predominantly our very large postings file, we focused on postings compression methods. We also used a subset of the actual dataset to compare compression results for better efficiency.

+--------------------------------+----------------+-------------------------+
| With subset of actual data     | dictionary.txt | postings.txt            |
+--------------------------------+----------------+-------------------------+
| Before Compression             | 7716760 bytes  | 14570330 bytes          |
+--------------------------------+----------------+-------------------------+
| Keeping normalised doc length  | -              | 14567794 bytes (-0.01%) |
| to 2 d.p. (previously could go |                |                         |
| up to 14 d.p.)                 |                |                         |
+--------------------------------+----------------+-------------------------+
| + Gap encoding for doc-IDs     | -              | 12750560 bytes (-12.4%) |
+--------------------------------+----------------+-------------------------+
| + Remove term freq and zero    | -              | 8625649 bytes (-40.7%)  |
| entries for zone term freq     |                |                         |
+--------------------------------+----------------+-------------------------+
| + Remove                       | -              | 8616382 bytes (-40.8%)  |
| Chinese/Korean/Japanese        |                |                         |
| (CJK) letters                  |                |                         |
+--------------------------------+----------------+-------------------------+
| + Remove stopwords             | -              | 8186275 bytes (-42.8%)  |
+--------------------------------+----------------+-------------------------+

After using the aforementioned postings compression technique and the removal of CJK terms and stopwords, we manage to achieve a significant saving in the postings file size (from 1.5GB to 591MB). However, the combined size of the dictionary and postings list was still too large to fit into the 800MB requirement.

We looked through the dictionary again and noticed that there were some strange characters being indexed, that were not in the CJK category (eg. ①, ≈). Hence, we decided to be more strict with validating word tokens, accepting only alphanumeric characters. This was deemed acceptable since queries are composed only of alphanumeric characters. Adopting this approach not only reduced the size of our dictionary, but also reduced the size of our postings list.

To reduce the size of our dictionary further, we removed the storage of the absolute offset of term postings lists. Instead, when reading the dictionary from file during searching, we use the accumulative offset (which is still stored during indexing) to calculate the absolute offset needed to retrieve the postings list.

+-----------------------------+------------------------+------------------------+
| With subset of actual data  | dictionary.txt         | postings.txt           |
+-----------------------------+------------------------+------------------------+
| Combined methods above      | -                      | 8186275 bytes          |
+-----------------------------+------------------------+------------------------+
| Accepting only alphanumeric | 7716760 bytes          | 6254979 bytes (-23.5%) |
| terms                       |                        |                        |
+-----------------------------+------------------------+------------------------+
| Using gap encoding          | 5317374 bytes (-31.0%) |                        |
| in dictionary for offsets   |                        |                        |
+-----------------------------+------------------------+------------------------+

Finally, adopting a set of all these methods allowed us to reduce the size of our postings to 558MB, a large improvement from our initial size of 1.5GB.

Searching
The preprocessing required are:
Reading and parsing dictionary_file using read_dict() to obtain the dictionary created in index.py
Dictionary parsed format: [doc_freq, absolute_offset, accumulative_offset]
Reading the postings_file using read_posting(), which is required for seeking within the posting list of query terms
Parsing of query using parse_query() to separate the query terms
Example query: “term1 term2 tem3 AND term4 term5 term6”
Parsed query format: [[term1, term2, term3],[term4, term5, term6]], the inner arrays are separated based on the logical AND

After preprocessing, we perform query expansion and pseudo relevance feedback on the parsed query. To get the final scores, we pass the expanded and refined query and a terms count dictionary containing <query_term:query_term_frequency> into calculate_cosine_scores().

In calculate_cosine_scores():

Before the actual calculation, we retrieve all the documents that fulfil the boolean requirements of the query. We perform logical AND to all the segments (i.e. inner arrays) from the aforementioned parsed query array. Within each segment, for phrasal queries that have more than two words, we will perform logical AND to the postings lists of each bi-word; otherwise, we will use logical OR to find the union of the posting lists of all terms within the segment. This gives us the main posting list.

For each of the query term:
Calculate the weight of the term in the query.
tf-idf equation: (1+log(tf)) * log(collection size/df)
Get the posting list from postings_file using the pointers (i.e. offsets) in dictionary_file and seek().
For each document retrieved from the posting list, calculate the weight of term in the document and perform the dot product of query weight and document weight if the doc id exists in the main posting list that we have obtained above.
tf equation:            	1+log(tf)
Dot product equation: 	sum(document weight * query weight) for each document
Score format:          	{doc_id1: score1, doc_id2: score2......}
Perform normalization on each of the documents' score
Equation: score/document length
Sort the document according to the score in descending order (and break tie in ascending order of doc_id) and store them in the sorted_score array
sorted_score format:    [doc_id1, doc_id2......]

Note for search.py:
When parsing the queries, all the query terms are tokenized (i.e. stemmed and case-folded to lower case). This is done in data.py.
For query terms that are not found in the dictionary, we will simply ignore them (i.e. they will not be considered in the calculation of the cosine scores).
No heuristics are used in search.py.
The weight of the documents is calculated using the equation below. The order of importance of the various zones are: title (most important), court, content and date. As we can see in the equation, a higher weightage is given to the more important zones.
Equation: doc_weight = a*(weight of title) + b*(weight of content) + c*(weight of date) + d*(weight of court)  such that a = 0.4708, b = 0.176471, c = 0.117647, d = 0.235294 and a + b + c + d = 1

Data
The functions included in data.py are mainly to support the search process. They include:
read_dict() and read_posting() to read the dictionary and postings that we have indexed respectively
get_postings_list() to retrieve the <doc_id, zone_tfs> entries
get_intermediate_postings() to retrieve only the <doc_id> entries
get_main_postings() to retrieve only the <doc_id> entries that fulfil the Boolean query
or_op() and and_op() to find the union and intersection of two sets of posting lists respectively

Utility
The functions included in utility.py help us to filter out and normalize the terms to be indexed into the dictionary.

Allocation of Workload
Indexing (mainly handled by A0189690L and A0190198W)
- Modify the processing of the dataset (in comparison to that in Homework 3)
- Include the zone information (i.e. zone term frequencies) and the removal of combined  
  term frequency of documents
- Include bi-words in addition to uni-words
- Implement pseudo relevance feedback for search
- Gap encoding for postings and dictionary files compression
- Filter the dictionary terms to remove CJK terms and stopwords

Searching (mainly handled by A0199786X and A0200679A)
- Modify the parsing of queries to support phrasal and boolean (i.e. AND) queries
- Include query expansion
- Modify the calculation of document weight to handle zone weighting
- Modify the calculation of cosine scores to support boolean queries
- Introduce additional functions and modifications to data.py to support searching

Note: The actual separation of workload is not as strictly defined as above, all team members have contributed to both phases of the project in one way or another.

== Files included with this submission ==

README.txt
Includes a description of the function implementations, design considerations and references

index.py
Includes the function implementation of build_index() (with other functions)

search.py
Includes the function implementation of run_search() (with other functions)

data.py
Includes all the functions related to the operation on getting/reading data from dictionary.txt and posting.txt

 utility.py
Includes utility functions shared by other modules (tokenizer)

dictionary.txt
Includes indexed terms, document frequencies, posting list accumulative offsets

postings.txt
Includes list of all documents (and their normalized lengths) and postings list

BONUS.docx
Includes the description and discussion of the query refinement techniques implemented

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0189690L-A0190198W-A0199786X-A0200679A, 
certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason: NIL

I suggest that I should be graded as follows: NIL

== References ==

Clarification regarding the use of zones during query processing
https://piazza.com/class/kjmny91pkrx6ag?cid=198
https://piazza.com/class/kjmny91pkrx6ag?cid=202
Usage of nltk wordnet
https://www.guru99.com/wordnet-nltk.html
Stopword removal
https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
