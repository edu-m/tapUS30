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
from datetime import datetime
from pyspark.sql import Window
from pyspark.sql import functions as F

sc = SparkContext(appName="tapUS30")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

names=["cgoods","financial","energy","health","industrial","tech"]
indexes=[Elasticsearch("http://es_cgoods:9200"),Elasticsearch("http://es_financial:9200"),Elasticsearch("http://es_energy:9200"),Elasticsearch("http://es_health:9200"),Elasticsearch("http://es_industrial:9200"),Elasticsearch("http://es_tech:9200")]
models=[]
day_in_ms = 86400000

for name in names:
    df = spark.read.json("/data/"+name)
    assembler = VectorAssembler(inputCols=['open','high','low'],outputCol='features')
    output = assembler.transform(df).select('features','close','tickerSymbol','timestamp')
    max_t = int(output.select(F.max("timestamp")).first()[0])
    lr = LinearRegression (featuresCol='features',labelCol='close',maxIter=10,regParam=0.3,elasticNetParam=0.8)
    trained_model = lr.fit(output)
    window_spec = Window.partitionBy("tickerSymbol").orderBy(col("timestamp").desc())
    df_with_row_number = df.withColumn("row_num", row_number().over(window_spec))

    # Filter the rows where the row number is less than or equal to 7
    result_df = df_with_row_number.filter(col("row_num") <= 7)  
    result_df = result_df.drop("row_num")
    result_df = result_df.groupBy("tickerSymbol").agg(F.avg("open").alias("avg(open)"),\
        F.avg("high").alias("avg(high)"),F.avg("low").alias("avg(low)"),F.avg("timestamp"))
    assembler = VectorAssembler(inputCols=['avg(open)','avg(high)','avg(low)'],outputCol='features')
    result_df = assembler.transform(result_df).select("features","tickerSymbol")
    predictions = trained_model.transform(result_df)
    all_columns = output.columns + predictions.columns
    merged_df = output.join(predictions, on=["tickerSymbol","features"],how="full")
    merged_df = merged_df.fillna({"timestamp": max_t+86400000})
    merged_df = merged_df.fillna({"close": 0})
    merged_df = merged_df.fillna({"prediction": 0})
    merged_df.filter(col("prediction").isNotNull()).show()
    lr.write().overwrite().save("/models/"+name)
    formatted_data = merged_df.groupBy("timestamp").avg("close","prediction").sort("timestamp").withColumn("timestamp",merged_df.timestamp / 1000).withColumn("timestamp", col("timestamp").cast(TimestampType())).\
    withColumn("timestamp",date_format(col("timestamp"),"yyyy-MM-dd")).withColumn("avg(close)",round(col("avg(close)"),2))
    models.append(formatted_data.toPandas().to_dict(orient="records"))

for i in range(len(indexes)):
    print(i)
    for j in range(len(models[i])):
        indexes[i].index(index=names[i], id=j,document=json.dumps(models[i][j]))
