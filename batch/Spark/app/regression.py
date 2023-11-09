from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import PipelineModel
from pyspark.ml.regression import LinearRegression
# from elasticsearch import Elasticsearch
import os
import json
import itertools

def data_regression(df):

