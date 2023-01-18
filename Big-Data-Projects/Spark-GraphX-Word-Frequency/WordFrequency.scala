package comp9313.proj2

/* Importing all the required modules */
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.rdd._

object Problem1 {

	/* This function will take as its input a line (an array of words) and it will return all the pairs 
	   and their count in the format ((w1, w2), count) where w1 occurs before w2 in the line.
	   It will also return the count of all pairs starting with same word in the format ((w1, *), count).
	   Character '*' indicates that this pair refers to the total cout which will be used to divide 
	   the count of each pair to get the actual relative frequency.
	*/
	def getPairs(arr: Array[String]): Array[(String, Int)] = { 
	
		val len = arr.length 
		
		/* Initializing the array pairs with the values of first pair of the line.
		   Without initializing, it gives error when I add values to an empty array.
		*/
		var pairs = Array((arr(0)+":*", 1)) 			// adding the "*" pair
		pairs = pairs ++: Array((arr(0)+":"+arr(1), 1)) 	// adding the actual pair
		
		/* Running two loops to get first and second words of each pair */
		for(i <- 0 to len-1) { 
			for (j<- i+1 to len-1 if (i>0 || j>1)) { // added the if condition to ignore the first pair which we used in initialization
			
				/* Adding the "*" pair to denotes the count of pairs starting with this word only */
				var strWord = arr(i)+":*" 
				pairs = pairs ++: Array((strWord, 1)) 				
				
				/* Adding the actual pair and their count to the pairs array. */
				var strPair = arr(i)+":"+arr(j) 
				pairs = pairs ++: Array((strPair, 1)) 
			} 
		} 
		pairs // returing the final pairs array containing all the word pairs
	} 

	def main(args: Array[String]) {
		val conf = new SparkConf().setAppName("Project2Frequency")
		val sc = new SparkContext(conf)
		
		/* Getting the input file and the output folder location from the command line arguments */
		val inputFileLocation = args(0)
		val outputFileLocation = args(1)
		
		/* Storing the input text file as an RDD */
		val inputData = sc.textFile(inputFileLocation)
		
		/* Splitting all the lines of the file into words */
		val lowerLines = inputData.map(line => line.split("[\\s*$&#/\"'\\,.:;?!\\[\\](){}<>~\\-_]+") // splitting as per given function
						.filter(word => word.length >=1) // storing only words which have a length of at least 1
						.map(word => word.toLowerCase()) // converting all the words to lower case
						.filter(word => word.charAt(0) >= 'a' && word.charAt(0) <= 'z')) // keeping only words starting with alphabets

		/* Filtering out lines which didn't have at least 2 words, which is the minimum required to form a pair */
		val filteredLines = lowerLines.filter(x => x.length > 1)
		
		/* Applying getPairs function to all the lines to get all the pair combinatios and their respective counts */
		val allPairs = filteredLines.flatMap(arr => getPairs(arr))

		/* Combining the count for each pair to get their total count */
		val reducedPairs = allPairs.reduceByKey(_+_)

		/* Creating a broadcast variable to get the count of all pairs which starts with the same word */
		val broadcastVar  = sc.broadcast(reducedPairs.filter(x => x._1.split(":")(1) == "*") // to check for pairs where 2nd word is "*"
							       .map(x => (x._1.split(":")(0), x._2)) //  storing the 1st word and its count
							       .collect.toMap) // collecting RDD to get an array and storing it as a Map collection

		/* To get only the valid word pairs, filtering out any "*" pairs */
		val onlyPairs = reducedPairs.filter(x => x._1.split(":")(1) != "*") // filtering out pairs where 2nd word is "*"
					     .map(x => (x._1.split(":")(0), x._1.split(":")(1), x._2)) // storing all pairs in the format (w1, w2, count)
		
		/* Calculating the relative frequency by dividing the pair count by the total count of word 1 pairs.
		   Broadcast variable is used to get the total count of all pairs staring with word 1.
		*/
		val finalValues = onlyPairs.map(x => (x._1, x._2, x._3.toDouble/broadcastVar.value(x._1)))
		
		/* Finally sorting all the pairs and their frequency and storing them in output location in the desired output format */
		finalValues.sortBy(x => (x._1, - x._3, x._2))
			    .map(x => x._1+" "+x._2+" "+x._3)
			    .saveAsTextFile(outputFileLocation)
		
		sc.stop()
	}
}
