from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark import SparkFiles
import pandas as pd
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import StringIndexer
import time

DATA = ["/data/cgoods/",
"/data/energy/",
"/data/financial/",
"/data/health/",
"/data/industrial/",
"/data/tech/"]
sc = SparkContext(appName="tapUS30")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

df = spark.read.json(DATA)

assembler = VectorAssembler(inputCols=['open','close','high','low'],outputCol='features')
output = assembler.transform(df).select('features','close')
splits = output.randomSplit([0.7,0.3])
train_df = splits[0]
test_df = splits[1]
lr = LinearRegression (featuresCol='features',labelCol='close',maxIter=10,regParam=0.3,elasticNetParam=0.8)
trained_model = lr.fit(train_df)
result = trained_model.summary
print("error: ",result.r2)

# predictions = trained_model.transform(output.select('features')).show(20)
predictions = trained_model.transform(test_df)
predictions.show()