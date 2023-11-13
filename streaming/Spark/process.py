from pyspark import SparkContext
import json
from pyspark.sql import SparkSession
from pyspark import SparkFiles
import pandas as pd
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from elasticsearch import Elasticsearch
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import StringIndexer
import time

sc = SparkContext(appName="tapUS30")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

names=["cgoods","financial","energy","health","industrial","tech"]
indexes=[Elasticsearch("http://es_cgoods:9200"),Elasticsearch("http://es_financial:9200"),Elasticsearch("http://es_energy:9200"),Elasticsearch("http://es_health:9200"),Elasticsearch("http://es_industrial:9200"),Elasticsearch("http://es_tech:9200")]
models=[]

for name in names:
    df = spark.read.json("/data/"+name)
    output = assembler.transform(df).select('features','close','tickerSymbol')
    lr = LinearRegression.load("/models/"+name)
    trained_model = lr.fit(output)
    predictions = trained_model.transform(output)
    predictions = predictions.select("close","prediction")
    models.append(predictions.toPandas().to_dict(orient="records"))

for i in range(len(indexes)):
    for j in range(len(models[i])):
        indexes[i].index(index=names[i], id=j,document=json.dumps(models[i][j]))
