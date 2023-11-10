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

# es_energy     = Elasticsearch("http://es_energy:9200")
# es_financial  = Elasticsearch("http://es_financial:9200")
# es_health     = Elasticsearch("http://es_health:9200")
# es_industrial = Elasticsearch("http://es_industrial:9200")
# es_tech       = Elasticsearch("http://es_tech:9200")

DATA = "/data/cgoods/"
sc = SparkContext(appName="tapUS30")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

df = spark.read.json(DATA)

assembler = VectorAssembler(inputCols=['open','high','low'],outputCol='features')
output = assembler.transform(df).select('features','close','tickerSymbol')
splits = output.randomSplit([0.7,0.3])
train_df = splits[0]
test_df = splits[1]
lr = LinearRegression (featuresCol='features',labelCol='close',maxIter=10,regParam=0.3,elasticNetParam=0.8)
trained_model = lr.fit(train_df)
# result = trained_model.summary
# print("error: ",result.r2)
doc = {
    'author': 'giovanny',
    'text': 'Elasticsearch: cool. bonsai cool.'
}
# predictions = trained_model.transform(output.select('features')).show(20)
predictions = trained_model.transform(output)
es_cgoods = Elasticsearch("http://es_cgoods:9200")
# es_cgoods.index(index="test",id=1,document=doc)
predictions = predictions.select("close","prediction")
cgoods_data = predictions.toPandas().to_dict(orient="records")
for i in range(len(cgoods_data)):
    es_cgoods.index(index='test', id=i,document=json.dumps(cgoods_data[i]))
# predictions.show()