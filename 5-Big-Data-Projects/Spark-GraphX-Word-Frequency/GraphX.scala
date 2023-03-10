package comp9313.proj2

/* Importing the required modules */
import org.apache.spark.graphx._
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD

object Problem2 {
	def main(args: Array[String]) = {
		val conf = new SparkConf().setAppName("Project2Triangles")
		val sc = new SparkContext(conf)
    
    		/* Getting input file and output folder locations from command line arguments */
		val inputFile = args(0)
		val outputFolder = args(1)
		
		/* Referring to 3 edges of triangle, it will determine the number of times pregel will run */
		val edgesInTriangle = 3
		
		/* Forming the graph from the input file */
		val edges = sc.textFile(inputFile)      
		val edgelist = edges.map(x => x.split(" ")).map(x=> Edge(x(1).toLong, x(2).toLong, 0.0))	
		val graph = Graph.fromEdges[Double, Double](edgelist, 0.0)

		/* Loading the initial graph which will be used to run pregel and store the passed data. 
		   Data will be stored in the form of a set of strings.
		*/
		val initialGraph = graph.mapVertices((id, _) => Set[String]())    
		
		/* Calling preger operator and it will be run 3 times which is required to reach all the vertices of a triangle */   
		val res = initialGraph.pregel(Set[String](), edgesInTriangle)(
		(id, ns, newns) => newns, // Vertex program: Only storing the last passed information which will contain all triangle vertices
		triplet => { /* Send message program:
				 For the 1st step, we will just send a string message to destination vertices
				 which will contain the source and destination IDs separated by the character '-'.
				 For next steps, we will add only the destination ID, separated by '-',
				 to all the previous received messages by a source vertex.
				 So, after the final 3rd run, we will have messages of the form v1-v2-v3-v4,
				 where v1 and v4 are same vertices, and v2 and v3 are different than v1 for it to form a triangle.
				 Using further operations, we will only store the strings which follow the required triangle format
				 and filter out all the other strings.
			     */
      
			val length = triplet.srcAttr.size
        
			if (length < 1) { // only for the 1st step
				Iterator((triplet.dstId, triplet.srcAttr+(triplet.srcId.toString+"-"+triplet.dstId.toString)))
			} else {	   // for all the next steps
				var srcAttr = triplet.srcAttr
				srcAttr = srcAttr.map(s => s+"-"+triplet.dstId.toString) // adding destination IDs to all the previous messages
				Iterator((triplet.dstId, srcAttr))
			}
      		},
		(a, b) => a++b // Merge message program: Just combining all the message sets into a single set
		)
    
    		/* Storing the data generated by pregel in a new RDD which will we used for further RDD transformations.
    		   Also, set of strings is converted to an array of strings as it provides more operations.
    		*/
		val pregelData = res.vertices.map{case(id, attr) => (id, attr.toArray)}	
		pregelData.persist() // persisting pregelData as it will be used for 3 different types of RDD transformations
		
		/* Filtering out vertices which didn't have any edge, so for them the array of strings was empty */
		val noTriangles_1 = pregelData.filter(x => x._2.length == 0)
		
		/* Filtering out vertices which did have some edges, but not enough to form a triangle.
		   So, their string format was like v1-v2 or v1-v2-v3 (but not the required v1-v2-v3-v4).
		*/
		val noTriangles_2 = pregelData.filter(x => x._2.length > 0) // initial check that array of strings is not empty
						.map(x => (x._1, x._2.filter(y => y.split("-").size >= 4))) // checking for required format
						.filter(x => x._2.length == 0) // checking if array becomes empty after removing invalid strings
    
		/* Only storing those strings which fit the required format v1-v2-v3-v4 */
		val cyclesData = pregelData.filter(x => x._2.length > 0)
						.map(x => (x._1, x._2.filter(y => y.split("-").size >= 4)))
						.filter(x => x._2.length > 0) // checking that array contains at least one string of required format
    		cyclesData.persist() // persisting cyclesData as it will be used to transform two RDDs
    		
    		/* Finally checking that v1=v4=source vertex and other vertices (v2 and v3) are different.
    		   If a string satisfies this format, it confirms that a triangle has been formed starting at source vertex v1.
    		*/
		val triangles = cyclesData.map(x => (x._1,x._2.filter(y => y.split("-")(0) == y.split("-")(3) && y.split("-")(0) != y.split("-")(1) 
						&& y.split("-")(0) != y.split("-")(2))))
						.filter(x => x._2.length > 0)
		
		/* Filtering out all vertices which doesn't satisfy the final triangle format */
		val noTriangles_3 = cyclesData.map(x => (x._1,x._2.filter(y => y.split("-")(0) == y.split("-")(3) && y.split("-")(0) != y.split("-")(1) 
						&& y.split("-")(0) != y.split("-")(2))))
						.filter(x => x._2.length == 0)
		
		/* Sorting all the strings by v2 and v3 numerically in descending order */
		val trianglesSorted = triangles.map(x => (x._1, x._2.sortBy(y => (- y.split("-")(1).toInt, - y.split("-")(2).toInt))))

		/* Storing all the string in the required printable format: v1->v2->v3; */
		val trianglesPrint = trianglesSorted.map(x => (x._1, x._2.map(y => y.split("-")(0)+"->"+y.split("-")(1)+"->"+y.split("-")(2)+";")))

		/* Combining all the strings into a single string */
		val trianglesCombine = trianglesPrint.map(x => (x._1, x._2.reduce((a, b) => a ++ b)))

		/* Finally adding ':' in front of vertex Id and combining all the triangle strings with it */
		val trianglesFinal = trianglesCombine.map(x => x._1.toString+":"+x._2) 
		
		/* Merging all the 3 types of filtered out vertices which didn't have any triangles */
		val allNoTriangles = noTriangles_1 ++ noTriangles_2 ++ noTriangles_3
		
		/* Adding a ':' to all the vertices with no triangles */
		val noTrianglesPrint = allNoTriangles.map(x => x._1.toString+":")
		
		/* Combining all the vertices with and without traingles into a single RDD */
		val allVertices = trianglesFinal ++ noTrianglesPrint

		/* Sorting the final data by vertices number and storing as text files in given output folder */
		allVertices.sortBy(x => x.split(":")(0).toInt).saveAsTextFile(outputFolder)
    
		sc.stop()
	}
}

