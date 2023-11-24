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
import time

spark = SparkSession.builder.appName("tapus30").getOrCreate()
sc = spark.sparkContext
sc.setLogLevel("ERROR")
indexes=[Elasticsearch("http://es_cgoods:9200"),Elasticsearch("http://es_financial:9200"),Elasticsearch("http://es_energy:9200"),Elasticsearch("http://es_health:9200"),Elasticsearch("http://es_industrial:9200"),Elasticsearch("http://es_tech:9200")]

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType
import time

topics = {
    "cgoods":0,
    "financial":1,
    "energy":2,
    "health":3,
    "industrial":4,
    "tech":5
}

number_of_items = {
    "cgoods":5,
    "financial":5,
    "energy":1,
    "health":6,
    "industrial":5,
    "tech":8
}

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
    .load().select(from_json(col("value").cast("string"), schema).alias("data"),col("topic").cast("string"))
    return df

def writeKafkaStreamingData(dataframes,topic):
    print("Executing "+topic+" thread...")
    dataframes[topics[topic]] = subscribeToTopic(dataframes,topic)

def save_and_send_data(data, name, es_index):
    for i in range(len(data)):
        for j in range(len(data[i])):
            json_dump = json.dumps(data[i][j])
            es_index.index(index=name+"_streaming", id=j,document=json_dump)

def load_indexes():
    for name in names: # Ricostituiamo i dati storici + previsioni fornite dal lato batch
        historical = open("/indexes/"+name+"_historical.txt")
        prediction = open("/indexes/"+name+"_prediction.txt")
        for line in historical:
            indexes[topics[name]].index(index=name+"_historical",document=json.loads(line),timeout="30s") 
        for line in prediction:
            indexes[topics[name]].index(index=name+"_prediction",document=json.loads(line),timeout="30s") 


averages = [1,2,3,4,5,6]
threads = []

for i in range(6):
    thread = threading.Thread(target=writeKafkaStreamingData, args=(dataframes,names[i]))
    threads.append(thread)

for thread in threads:
    thread.start()

historical_data = []

time.sleep(15) # Diamo tempo ai container di avviarsi

load_indexes()

for i in range(6):
    averages[i] = dataframes[i].select(col("data.close"),col("data.timestamp"),col("topic"))
    # averages[i].printSchema()
    averages[i] = averages[i].groupBy("timestamp").avg("close").sort("timestamp").withColumn("timestamp",averages[i].timestamp / 1000).withColumn("timestamp", date_format(col("timestamp").cast(TimestampType()), "yyyy-MM-dd'T'HH:mm:ss.SSSZ")).withColumn("avg(close)",round(col("avg(close)"),2))
    averages[i] = averages[i].writeStream.outputMode("complete").queryName(names[i]).format("memory").start()
while(True):
    for i in range(6):
        temp_sdf = spark.sql("SELECT * FROM "+names[i])
        if temp_sdf.count() > 0:
            temp_sdf.show()
            historical_data.append(temp_sdf.toPandas().to_dict(orient="records"))
            save_and_send_data(historical_data,names[i],indexes[i])
