from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark import SparkFiles
from pyspark.sql.functions import *
from pyspark.sql.types import *

KAFKA_BOOTSTRAP_SERVERS = "tap:9092"
sc = SparkContext(appName="tapUS30")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

dt = spark \
     .readStream \
     .format("kafka") \
     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
     .option("subscribe", "financial").option("startingOffsets", "earliest") \
     .load()

#Schema for the dataframe 
data_schema = StructType().add("v", IntegerType()) \
     .add("vw", FloatType()).add("o", FloatType()).add("c", FloatType()) \
     .add("h", FloatType()).add("l", FloatType()).add("t", IntegerType()) \
     .add("n", IntegerType()).add("tickerSymbol", StringType())\
     .add("volume",IntegerType()).add("open", FloatType()).add("close", FloatType()).add("high", FloatType())\
     .add("low", FloatType()).add("timestamp", IntegerType()).add("numberOfItems", IntegerType())

#Extract the values from the dataframe in streaming  
data_received = dt.selectExpr("CAST(value AS STRING)") \
     .select(from_json(col("volume"), data_schema).alias("data_received")) \
     .select("data_received.*")

print(data_received);