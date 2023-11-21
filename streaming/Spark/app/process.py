from pyspark import SparkContext
import json
from pyspark.sql import SparkSession
from pyspark import SparkFiles
import pandas as pd
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.functions import vector_to_array
from pyspark.ml.linalg import Vectors
from pyspark.sql.types import TimestampType
from pyspark.ml.feature import VectorAssembler
from elasticsearch import Elasticsearch
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import StringIndexer
import datetime
from pyspark.sql import Window
from pyspark.sql import functions as F
import threading
import heapq

# sc = SparkContext(appName="tapUS30")
spark = SparkSession.builder.master('local[*]').config("spark.driver.memory","15g")\
    .appName("tapus30").getOrCreate()
# # spark = SparkSession(sc)
sc = spark.sparkContext
sc.setLogLevel("WARN")

# names=["cgoods","financial","energy","health","industrial","tech"]
# indexes=[Elasticsearch("http://es_cgoods:9200"),Elasticsearch("http://es_financial:9200"),Elasticsearch("http://es_energy:9200"),Elasticsearch("http://es_health:9200"),Elasticsearch("http://es_industrial:9200"),Elasticsearch("http://es_tech:9200")]
# prediction_data=[]
# historical_data=[]
# day_in_ms = 86400000
# window_size = 10

# # Format data to conform dataframe to es timestamp & column names
# """
#     First, we group all tuples by their timestamp, which is specified in millisecond epoch time 
#     In this way we obtain a structure containing each tuple for each company grouped by the timestamp
#     so that every tuple, from each company is aligned in respect to its day.

#     Doing so allows us to average the data for each day, reducing it to one tuple for each day.
#     We then convert the timestamp to a date in the format year-month-day, using an appropriate function
#     (we must remember to divide the timestamp by 1000 because 'cast(TimestampType()))' expects the
#     timestamp in seconds.

#     At the end of the processing, we round down the data in the close/prediction columns to two decimal
#     places for consistency (not all data from the API has the same amount of precision)
#     and ease of visualiation.
# """
# def format_data(dataframe, close_name):
#     return dataframe.groupBy("timestamp").avg(close_name).sort("timestamp").withColumn("timestamp",predictions.timestamp / 1000).withColumn("timestamp", col("timestamp").cast(TimestampType())).\
#     withColumn("timestamp",date_format(col("timestamp"),"yyyy-MM-dd")).withColumn("avg("+close_name+")",round(col("avg("+close_name+")"),2))
    
# # Convert epoch time to a datetime object
# def epoch_ms_to_weekday(epoch_time_in_ms):
#     dt_object = datetime.datetime.fromtimestamp(epoch_time_in_ms/1000)
#     # Get the weekday as an integer (Monday is 0 and Sunday is 6)
#     weekday_number = dt_object.weekday()
#     return weekday_number

# # Specification for window with order in respect to timestamp for each tickerSymbol
# # def prediction(dataframe, model, prediction=None, nIter=window_size):
    

# def save_and_send_data(scope, data, name, es_index):
#     file = open("/indexes/"+name+"_"+scope+".txt","w")
#     for j in range(len(data[i])):
#         json_dump = json.dumps(data[i][j])
#         file.write(json_dump+"\n") # Write each element in a new line
#         es_index.index(index=name+"_"+scope, id=j,document=json_dump)
#     file.close()



# for name in names:
#     df = spark \
#     .readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "k-cgoods:9092,k-energy:9092,k-financial:9092,k-health:9092,k-industrial:9092,k-tech:9092") \
#     .option("subscribe", name) \
#     .load()
#     df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "CAST(topic AS STRING)")
#     value = df.select("value","topic")

#     query = value.writeStream.outputMode("append").format("console").start()

#     query.awaitTermination()

#     lr = LinearRegression (featuresCol='features',labelCol='close',maxIter=10,regParam=0.3,elasticNetParam=0.7)
#     lr.load("/models/"+name)
    
#     trained_model = lr.fit(output)
#     print("processing data for "+name+"...")
#     # Performs the recursive prediction based on the trained_model that we have just created
#         # predictions = recursive_prediction(df, trained_model)
#     print("...done")
    
#     historical_data.append(format_data(output,"close").toPandas().to_dict(orient="records"))
#     prediction_data.append(format_data(predictions.withColumnRenamed("close","prediction"),"prediction").toPandas().to_dict(orient="records"))

# # Finally, we can send the data to elasticsearch
# # We'll also need to save the formatted index data
# # to make it available to the streaming process
# for i in range(len(indexes)):
#     print("sending index "+names[i]+" to elasticsearch...")
#     save_and_send_data("prediction",prediction_data,names[i],indexes[i])
#     save_and_send_data("historical",historical_data,names[i],indexes[i])


from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType
import time
time.sleep(15)

topics = {
    "cgoods":0,
    "financial":1,
    "energy":2,
    "health":3,
    "industrial":4,
    "tech":5
}

# Creare una sessione Spark
spark = SparkSession.builder \
    .appName("KafkaToDataFrame") \
    .getOrCreate()

# Definire lo schema dei dati
schema = StructType([
    StructField("v", LongType(), True),
    StructField("vw", DoubleType(), True),
    StructField("o", DoubleType(), True),
    StructField("c", DoubleType(), True),
    StructField("h", DoubleType(), True),
    StructField("l", DoubleType(), True),
    StructField("t", LongType(), True),
    StructField("n", LongType(), True),
    StructField("tickerSymbol", StringType(), True),
    StructField("volume", LongType(), True),
    StructField("open", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("timestamp", LongType(), True),
    StructField("numberOfItems", LongType(), True)
])

# Definire i topic di Kafka da cui leggere i dati
names=["cgoods","financial","energy","health","industrial","tech"]

# Creare un DataFrame per ogni topic
dataframes = [0,1,2,3,4,5]

def get_name_key(df):
    return df['topic']

def subscribeToTopic(dataframes,topic):
    df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "k-cgoods:9092,k-energy:9092,k-financial:9092,k-health:9092,k-industrial:9092,k-tech:9092") \
    .option("subscribe", topic) \
    .load()
    # Estrai i dati dalla colonna "value" come stringa JSON e convertili in colonne
    parsed_df = df \
        .select(from_json(col("value").cast("string"), schema).alias("data"),col("topic").cast("string")) \
    # Aggiungi il DataFrame al elenco dei DataFrame
    return parsed_df

def writeKafkaStreamingData(dataframes,topic):
    dataframes[topics[topic]] = subscribeToTopic(dataframes,topic)
    query = dataframes[topics[topic]].writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
    query.awaitTermination()

threads = []
for i in range(6):
    thread = threading.Thread(target=writeKafkaStreamingData, args=(dataframes,names[i]))
    threads.append(thread)

for thread in threads:
    thread.start()
# Attendi che lo streaming termini
