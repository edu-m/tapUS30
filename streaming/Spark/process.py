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

sc = SparkContext(appName="tapUS30")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

names=["cgoods","financial","energy","health","industrial","tech"]
indexes=[Elasticsearch("http://es_cgoods:9200"),Elasticsearch("http://es_financial:9200"),Elasticsearch("http://es_energy:9200"),Elasticsearch("http://es_health:9200"),Elasticsearch("http://es_industrial:9200"),Elasticsearch("http://es_tech:9200")]
prediction_data=[]
historical_data=[]
day_in_ms = 86400000
window_size = 10

def format_data(dataframe, close_name):
    return dataframe.groupBy("timestamp").avg(close_name).sort("timestamp").withColumn("timestamp",predictions.timestamp / 1000).withColumn("timestamp", col("timestamp").cast(TimestampType())).\
    withColumn("timestamp",date_format(col("timestamp"),"yyyy-MM-dd")).withColumn("avg("+close_name+")",round(col("avg("+close_name+")"),2))
    
def epoch_ms_to_weekday(epoch_time_in_ms):
    # Convert epoch time to a datetime object
    dt_object = datetime.datetime.fromtimestamp(epoch_time_in_ms/1000)
    # Get the weekday as an integer (Monday is 0 and Sunday is 6)
    weekday_number = dt_object.weekday()
    return weekday_number

def recursive_prediction(dataframe, model, prediction=None, nIter=window_size):
    # specifica per la vista con ordinamento su timestamp per ciascun tickerSymbol
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
        print("Completion "+str(((window_size-nIter+1)/window_size)*100)+"%")
        prediction = prediction.withColumn("timestamp",lit(max_t+day_offset))
        result_df = result_df.union(prediction.withColumnRenamed("prediction","close").select("tickerSymbol","open","high","low","timestamp"\
        ,"close")).distinct()
        nIter = nIter - 1
    prediction = trained_model.transform(temp_df).select("tickerSymbol","open","high","low","timestamp","prediction","features")
    if nIter == 0 and result_df is not None:
        return result_df
    else:
        return recursive_prediction(dataframe=result_df,model=trained_model,prediction=prediction,nIter=nIter)

for name in names:
    df = spark.read.json("/data/"+name)
    assembler = VectorAssembler(inputCols=['open','high','low'],outputCol='features')
    output = assembler.transform(df).select('features','close','tickerSymbol','timestamp')
    lr = LinearRegression (featuresCol='features',labelCol='close',maxIter=10,regParam=0.3,elasticNetParam=0.7)
    trained_model = lr.fit(output)
    print("processing data for "+name+"...")
    predictions = recursive_prediction(df, trained_model)
    print("...done")
    lr.write().overwrite().save("/models/"+name)
    historical_data.append(format_data(output,"close").toPandas().to_dict(orient="records"))
    prediction_data.append(format_data(predictions.withColumnRenamed("close","prediction"),"prediction").toPandas().to_dict(orient="records"))

for i in range(len(indexes)):
    print("sending index "+names[i]+" to elasticsearch...")
    for j in range(len(prediction_data[i])):
        indexes[i].index(index=names[i]+"_prediction", id=j,document=json.dumps(prediction_data[i][j]))
    for k in range(len(historical_data[i])):
        indexes[i].index(index=names[i]+"_historical", id=k,document=json.dumps(historical_data[i][k]))
