package comp9313.proj3

/* Importing all the required modules */
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.rdd._

object SetSimJoin {	
	
	def main(args: Array[String]) {
		
		// Part 0: Initializing Spark parameters and loading arguments from command line
		
		/* Configuring the Spark context object. */
		val conf = new SparkConf().setAppName("Project3")
		val sc = new SparkContext(conf)		
		
		/* Getting the input file, output folder location and the similarity threshold value from the command line arguments. */
		val inputFileLocation = args(0)
		val outputFileLocation = args(1)
		val tau = args(2).toDouble
		
		
		// Part 1: Processing the input file and extracting all the tokens
		
		/* Storing the input text file as an RDD. */
		val inputData = sc.textFile(inputFileLocation)
		
		/* Splitting each input line (record) to numbers and storing them as 'Integer' format. */
		val lines = inputData.map(line => line.split(" ").map(x => x.toInt))
		
		/* Converting each record into a (key-value) pair where key is the Record ID and value is an array of all token IDs in that record. */
		val kvPairs = lines.map(x => (x(0), x.drop(1)))

		/* Extracting tokens from all the records as (key-value) pairs and storing them in a single array RDD.
		   Here, key is the token ID and value is the total count of that token. Initially, counts are stored as 1 for each token in a record
		   and then all the counts are accumulated to get the total count of a token in the whole file.
		*/
		val tokenCount = kvPairs.flatMap(x => x._2.map(y => (y,1))).reduceByKey(_+_)
		
		/* All the (token-count) pairs are stored as a Map type collection in a broadcast variable. */
		val broadcastTokens  = sc.broadcast(tokenCount.collectAsMap)
		
		
		// Part 2: Calculating prefixes for each record
		
		/* Replacing the token with the (token-count) key-value pair in each record that we stored earlier. 
		   This count is the total count of the token in the whole document obtained from the broadcast Map variable.
		   Now, this RDD has a key-value pair structure as (K1, Array( (K2, V2) )), where K1 is the record ID and
		   value is an array of key-values pairs of token IDs and their count.
		*/
		val recordsFreq = kvPairs.map(x => (x._1, x._2.map(y => (y, broadcastTokens.value(y)))))
		
		/* Sorted all the token IDs in each record using their counts and finally stored only the token ID (discarding the count).
		   All the tokens were sorted first with their count and then by token ID itself.
		*/
		val sortedRecords = recordsFreq.map(x => (x._1, x._2.sortBy(y => (y._2, y._1)).map(z => z._1)))
		
		/* Identified the prefix tokens for each record using the provided similarity threshold value. The idea is that
		   we can find the prefix length by subtracting record_length*threshold value from the record length.
		   Also, I multipled by threshold-0.01 to consider the edge case of prefix length.
		   I added index to the sorted token IDs, filtered only the first few takens identified by the formula, and
		   then discarded the index to store only the token IDs as prefixes in a 3-tuple format. 1st element of the 3-tuple
		   is the record ID, 2nd tuple is the array containing all tokens and 3rd element is the array of prefix tokens.
		*/
		val prefixes = sortedRecords.map(x => (x._1, x._2, x._2.zipWithIndex.filter(y => y._2<(x._2.length-(x._2.length*(tau-0.01)).toInt)).map(y => y._1)))		
		
		/* Unpersisting the broadcast variable for tokens frequency as it is not required anymore */
		broadcastTokens.unpersist() 

	
		// Part 3: Extracting the candidate pairs from prefixes list and filtering out the invalid pairs
		
		/* Now, we extract all the prefixes and the records as (key-value) pairs where key is the prefix token ID
		   and value is an array of (key2-value2) pairs where key2 is record ID and value2 is the array of tokens for that record.
		*/
		val prefixIDs = prefixes.flatMap(x => x._3.map(y => (y, Array((x._1, x._2))))) 
	
		/* Applied the reduceByKey function to combine all the (recordID-all tokens) pairs for each prefix token.
		   This combined all the records sharing a same token into a single array.
		   Then discarded the prefix token ID and stored only the array of all (recordID-all tokens).
		   Filtered out those arrays whose length is only one as these records won't be matched with 
		   any other record under this prefix token.
		   Each element of this RDD is an array, which contains more than one (recordID-all tokens) pairs.
		*/
		val prefixIDsCombined = prefixIDs.reduceByKey(_++_).map(x => x._2).filter(x => x.length > 1)
		
		/* Identified all the candidate pairs by going through all the elements (arrays) of the previous RDD and
		   combining every pair of that array and storing all the candidate pairs in a single array.
		   At the same time, we only kept candidate pairs where the first record ID < second record ID.
		   Also, filtered out any pair where length of smallest record divided by length of largest record is less
		   then threshold value as their similarity would always be less than the threshold.
		   So, each element of this RDD is a key-value pair of the form ( (recordID 1, all_tokens), (recordID 2, all tokens)),
		   where record IDs 1 and 2 forms a candidate pair.
		*/
		val candidatePairs = prefixIDsCombined.flatMap(x => x.flatMap(y => x.map(z => (y, z)).filter(w => w._1._1 < w._2._1 && w._1._2.length.min(w._2._2.length) > (tau-0.01) * w._1._2.length.max(w._2._2.length))))
		
		
		// Part 4: Calculating the Jaccard Similarity of the pairs and saving the the results to the given output location
		
		/* Calculating Jaccard similarity value for all the candidate pairs. I modified the formula sim(a, b) = (a intersection b) / (a union b)
		   to (|a| + |b| - a union b) / (a union b) = ((|a| + |b|) / a union b) - 1 and used it to calculate Jaccard similarity as
		   it needs to do less calculation and is faster. I used union.distinct to find the union with only unique elements.
		*/
		val pairsSim = candidatePairs.map(x => (x._1._1, x._2._1,((x._1._2.length.toDouble + x._2._2.length)/x._1._2.union(x._2._2).distinct.size)-1))
		
		/* Filtering out pairs for which the similarity is below the threshold and keeping only the unique records. */
		val finalSimPairs = pairsSim.filter(x => (x._3-tau) >= -0.0000000001).distinct
		
		/* Finally sorting all the record pairs by record 1 then record 2 and saving in the desired output format. */
		finalSimPairs.sortBy(x => (x._1, x._2))
			    .map(x => "("+x._1+","+x._2+")\t"+x._3)
			    .saveAsTextFile(outputFileLocation)
		
		sc.stop()
	}
	
}
