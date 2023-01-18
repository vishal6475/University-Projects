# importing all the required modules for this program
from mrjob.job import MRJob
from mrjob.compat import jobconf_from_env
import re
import math

class WeightInvertedIndex(MRJob):
    """
    Weight Inverted Index class which contains definitions of mapper and reducer methods
    to calculate TF IDF weight of each word in the whole file.
    """

    def mapper(self, _, line):
        """
        This mapper method calculates and yields frequency of each word within a document using the in-mapper combiner method.
        Also, the dictionary 'freq' used for in-mapper combining is not stored in the memory, so it is memory efficient.
        """
        words = re.split("[ *$&#/\t\n\f\"\'\\,.:;?!\[\](){}<>~\-_]", line.strip().lower())		# to split the input line into different words
        
        docid = words[0]					# obtain the document id from the document (line)        
        freq = {}						# dictionary freq is used to store count of each word in a document
        for word in words[1:]:				# checks all the words except the first word (i.e. doc id)
        	if len(word):					# only checks words having length greater then zero
                    freq[word] = freq.get(word, 0) + 1	# increment count by one for each word occurrence

        for word, count in freq.items():			# iterate over all the (word, count) pairs of a single document
            yield word+','+str(docid), str(count)		# yield the docid and count for each word
            yield word+','+str('*'), str(1)			# yield the special '*' symbol to mark one document count for each word

    def reducer_init(self):
        """
        Defining the variables to be used for TF IDF calculation for a word.
        The dictionary 'docFreq' stores the count of only one word at a time and is extremely memory efficient.
        """
        self.docFreq = {}					# to store the number of documents in which a word appeared 
        self.docNumber = int(jobconf_from_env('myjob.settings.docnumber'))

    def reducer(self, key, values):   
        """
        This reducer method first calculates the document frequency of a word using the special '*' pair.
        For each word, '*' pair containing the occurrences of a word in different documents will come first.
        The frequency will be calculated from it and will be used for TF IDF calculation for all doc ids that will
        come later for this word. But when the next word comes, we will make this dictionary empty as we won't
        need the frequency of the older words as we had already calculated the TF IDF for each doc id for these words. 
        So, 'docFreq' only stores one word and its count at any point.
        """     
        word, docID = key.split(',')				# split the key into two parts to get word and doc id
        
        if docID == '*':					# checks for the special case '*'
            self.docFreq = {}					# emptying the dictionary 
            self.docFreq[word]  = int(len(list(values)))	# calculating the number of documents in which the word appeared
        else:
            for docCount in values:				# getting the count of a word within a document
                tfidf = int(docCount) * math.log((self.docNumber/self.docFreq.get(word, 1)), 10)
                yield word, str(docID)+', '+str(tfidf)	# yield the calculated tfidf value for each word, docid combination

    SORT_VALUES = True
        
    JOBCONF = {
    'mapreduce.map.output.key.field.separator': ',',				# defining the separator for key field
    'mapreduce.partition.keypartitioner.options':'-k1,1',			# to send the keys with same words to same reducer
    'partitioner':'org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner',
    'mapreduce.job.output.key.comparator.class':'org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator',
    'mapreduce.partition.keycomparator.options':'-k1,1 -k2,2n'		# to sort the keys on the basis of words and then docid numerically
    }

if __name__ == '__main__':
    WeightInvertedIndex.run()

