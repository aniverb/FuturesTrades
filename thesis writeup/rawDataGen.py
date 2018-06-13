#Jupyter Notebook Code: NOT MEANT TO BE EXECUTABLE

import matplotlib.pyplot as plt
%matplotlib inline
#%pylab inline
import numpy as np
import pandas as pd
from os import listdir
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext, DataFrame, HiveContext 
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler	
from pyspark.ml.clustering import KMeans

sconf = SparkConf().setMaster("local[32]").setAppName("TradeDataCount")\
.set("spark.driver.maxResultSize", "16g").set("spark.shuffle.consolidateFiles", "true") #spark://10.160.5.48:7077 or local[*] to use as many threads as cores
sc = SparkContext(conf=sconf)
#sqlContext = SQLContext(sc)
sqlContext = HiveContext(sc) #really hc

files = [f for f in listdir('/home/dnaiman1/findata/big_harvest') if 'Trades' in f]
paths=['/home/dnaiman1/findata/big_harvest/%s' % i for i in files]

def parseData(file_path):
    customSchema = StructType([ \
    StructField("ProductName", StringType(), True), \
    StructField("Maturity", StringType(), True), \
    StructField("Date", StringType(), True), \
    StructField("Time", StringType(), True), \
    StructField("Price", DoubleType(), True), \
    StructField("Quantity", IntegerType(), True)])
    
    df = (sqlContext
        .read.format('com.databricks.spark.csv')
        .options(header='false')
        .load(file_path, schema=customSchema))
    
    def maturityConv(date):
        elements=date.split("/")
        return "%s-%s-%s" % (elements[2], elements[0], elements[1])
    
    maturityConvUDF=udf(maturityConv, StringType())
    
    def dateConv(date):
        elements=date.split(":")
        return "%s-%s-%s" % (elements[0], elements[1], elements[2])

    dateConvUDF=udf(dateConv, StringType())
    
    def timeConv(time):
        return time[0:-4]

    timeConvUDF=udf(timeConv, StringType())
    
    df2=(df
     .withColumn("MaturityConv", maturityConvUDF(df.Maturity))
     .withColumn("DateConv", dateConvUDF(df.Date))
     .withColumn("TimeConv", timeConvUDF(df.Time)))
    
    df3=(df2
    .select(['ProductName', col('MaturityConv').cast('date').alias('Maturity'), col('DateConv').cast('date').alias('Date'), concat_ws(' ', df2.DateConv, df2.TimeConv)
    .alias('TimeStamp').cast('timestamp'), 'Price', 'Quantity'])) #can also use to_date('MaturityConv').alias('Maturity')
    
    return df3    
    
parsed_data=[]
for file in paths[8:]:
    parsed_data.append(parseData(file))
    
def union(data_list):
    unionDF=data_list[0].unionAll(data_list[1])
    for df in data_list[2:]:
        unionDF=unionDF.unionAll(df)
    return unionDF
    
data=union(parsed_data).cache() 

print "Raw data is %d rows." % data.count() #takes long b/c count action initiates caching process

max_date=data.select(max('Date')).first()
print "Max date is %s." % max_date

data.show()

data.rdd.saveAsPickleFile('raw_dataset_rdd.pickle') #python equivalent of saveAsObjectFile()
sc.stop()

