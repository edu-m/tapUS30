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

# sc = SparkContext(appName="tapUS30")
spark = SparkSession.builder.master('local[*]').config("spark.driver.memory","15g")\
    .appName("tapus30").getOrCreate()
# spark = SparkSession(sc)
sc = spark.sparkContext
sc.setLogLevel("WARN")

names=["cgoods","financial","energy","health","industrial","tech"]
indexes=[Elasticsearch("http://es_cgoods:9200"),Elasticsearch("http://es_financial:9200"),Elasticsearch("http://es_energy:9200"),Elasticsearch("http://es_health:9200"),Elasticsearch("http://es_industrial:9200"),Elasticsearch("http://es_tech:9200")]
prediction_data=[]
historical_data=[]
day_in_ms = 86400000
window_size = 12

# Format data to conform dataframe to es timestamp & column names
"""
    First, we group all tuples by their timestamp, which is specified in millisecond epoch time 
    In this way we obtain a structure containing each tuple for each company grouped by the timestamp
    so that every tuple, from each company is aligned in respect to its day.

    Doing so allows us to average the data for each day, reducing it to one tuple for each day.
    We then convert the timestamp to a date in the format year-month-day, using an appropriate function
    (we must remember to divide the timestamp by 1000 because 'cast(TimestampType()))' expects the
    timestamp in seconds.

    At the end of the processing, we round down the data in the close/prediction columns to two decimal
    places for consistency (not all data from the API has the same amount of precision)
    and ease of visualiation.
"""
def format_data(dataframe, close_name):
    return dataframe.groupBy("timestamp").avg(close_name).sort("timestamp").withColumn("timestamp",predictions.timestamp / 1000).withColumn("timestamp", col("timestamp").cast(TimestampType())).\
    withColumn("timestamp",date_format(col("timestamp"),"yyyy-MM-dd")).withColumn("avg("+close_name+")",round(col("avg("+close_name+")"),2))
    
# Convert epoch time to a datetime object
def epoch_ms_to_weekday(epoch_time_in_ms):
    dt_object = datetime.datetime.fromtimestamp(epoch_time_in_ms/1000)
    # Get the weekday as an integer (Monday is 0 and Sunday is 6)
    weekday_number = dt_object.weekday()
    return weekday_number

# Specification for window with order in respect to timestamp for each tickerSymbol
def recursive_prediction(dataframe, model, prediction=None, nIter=window_size):
    max_t = int(dataframe.select(F.max("timestamp")).first()[0])
    curr_weekday = epoch_ms_to_weekday(max_t+day_in_ms)
    day_offset = day_in_ms
    if curr_weekday > 4:
        day_offset = day_offset*(8-curr_weekday)
    
    window_spec = Window.partitionBy("tickerSymbol").orderBy(col("timestamp").desc())
    df_with_row_number = dataframe.withColumn("row_num", row_number().over(window_spec)).select("tickerSymbol","open","high","low","timestamp","close")
    result_df = df_with_row_number.filter(col("row_num") < window_size).drop("row_num")
    temp_df = result_df.groupBy("tickerSymbol").agg(F.avg("open").alias("open"),F.avg("high").alias("high"),F.avg("low").alias("low"),F.any_value("timestamp").alias("timestamp"),F.avg("close").alias("close"))
    assembler = VectorAssembler(inputCols=['open','high','low'],outputCol='features')
    temp_df = assembler.transform(temp_df)

    if(prediction != None):
        print("Completion "+str(int(((window_size-nIter+1)/window_size)*100))+"%")
        prediction = prediction.withColumn("timestamp",lit(max_t+day_offset))
        result_df = result_df.union(prediction.withColumnRenamed("prediction","close").select("tickerSymbol","open","high","low","timestamp"\
        ,"close")).distinct()
        nIter = nIter - 1
    prediction = trained_model.transform(temp_df).select("tickerSymbol","open","high","low","timestamp","prediction","features")
    if nIter == 0 and result_df is not None:
        return result_df
    else:
        return recursive_prediction(dataframe=result_df,model=trained_model,prediction=prediction,nIter=nIter)

def save_and_send_data(scope, data, name, es_index):
    file = open("/indexes/"+name+"_"+scope+".txt","w")
    for j in range(len(data[i])):
        json_dump = json.dumps(data[i][j])
        file.write(json_dump+"\n") # Write each element in a new line
        es_index.index(index=name+"_"+scope, id=j,document=json_dump)
    file.close()

for name in names:
    df = spark.read.json("/data/"+name)
    assembler = VectorAssembler(inputCols=['open','high','low'],outputCol='features')
    output = assembler.transform(df).select('features','close','tickerSymbol','timestamp')
    lr = LinearRegression (featuresCol='features',labelCol='close',maxIter=10,regParam=0.3,elasticNetParam=0.7)
    trained_model = lr.fit(output)
    print("processing data for "+name+"...")
    # Performs the recursive prediction based on the trained_model that we have just created
    predictions = recursive_prediction(df, trained_model)
    print("...done")
    # If we have previously executed the batch process (this file), 
    # we have to overwrite the model with fresh data
    lr.write().overwrite().save("/models/"+name)
    historical_data.append(format_data(output,"close").toPandas().to_dict(orient="records"))
    prediction_data.append(format_data(predictions.withColumnRenamed("close","prediction"),"prediction").toPandas().to_dict(orient="records"))

# Finally, we can send the data to elasticsearch
# We'll also need to save the formatted index data
# to make it available to the streaming process
for i in range(len(indexes)):
    print("sending index "+names[i]+" to elasticsearch...")
    save_and_send_data("prediction",prediction_data,names[i],indexes[i])
    save_and_send_data("historical",historical_data,names[i],indexes[i])