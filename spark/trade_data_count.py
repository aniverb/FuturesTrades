# coding: utf-8

# In[1]:
import numpy as np
import pandas as pd
from os import listdir

from pyspark import SparkContext
from pyspark.sql import SQLContext, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

if __name__ == "__main__":

    sc = SparkContext(appName="TradeDataCount")
    sqlContext = SQLContext(sc)


# In[3]:

    files = [f for f in listdir('/home/dnaiman1/findata/big_harvest') if 'Trades' in f]
    paths=['/home/dnaiman1/findata/big_harvest/%s' % i for i in files]


# In[4]:

    def parseData(file_path):
        customSchema = StructType([     StructField("ProductName", StringType(), True),     StructField("Maturity", StringType(), True),     StructField("Date", StringType(), True),     StructField("Time", StringType(), True),     StructField("Price", DoubleType(), True),     StructField("Quantity", IntegerType(), True)])
    
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
   	    .select(['ProductName', col('MaturityConv').cast('date').alias('Maturity'), col('DateConv').cast('date').alias('Date'), concat_ws(' ', df2.DateConv, df2.TimeConv).alias('TimeStamp').cast('timestamp'), 'Price', 'Quantity'])) #can also use to_date('MaturityConv').alias('Maturity')
    
        return df3


# In[5]:

    parsed_data=[]
    for file in paths[8:]:
        parsed_data.append(parseData(file))


# In[6]:

    def union(data_list):
    	unionDF=data_list[0].unionAll(data_list[1])
    	for df in data_list[2:]:
            unionDF=unionDF.unionAll(df)
    	return unionDF
    
    data=union(parsed_data).cache() 
    print("Raw data is %d rows." % data.count())


# In[7]:

    max_date=data.select(max('Date')).first()
    print("Max date is %s." % max_date)


# In[9]:

    data=data.select(['ProductName', 'Maturity', 'Date', 'TimeStamp', hour("TimeStamp").alias("Hour"), 'Price', 'Quantity'])


# In[14]:

    pivot=(data
 	.groupBy("ProductName", "Maturity", "Date")     
  	.pivot("Hour")
  	.agg(sum("Quantity"))
  	.orderBy("ProductName", "Maturity", "Date")       
  	.na.fill(0)
  	.cache())
  
    print("Pivoted data is %d rows." % pivot.count())


# In[15]:

    pivotDF=pivot.toPandas()
    pivotDF['DayTotal'] = pivotDF.sum(axis=1)
    pivotDF.to_csv("trades_pivot_%s.txt" % max_date, sep='\t', index=False)
    print("File trades_pivot_%s.txt written to disk." % max_date)


# In[16]:

    pivot.registerTempTable("Trades")
    productList = sqlContext.sql("select distinct ProductName, Maturity from Trades group by ProductName, Maturity order by ProductName, Maturity")
    print("Number of unique products (instrument/maturity pairs) are %d." % productList.count())


# In[17]:

    products=productList.toPandas()
    products.to_csv("product_list_%s.txt" % max_date, sep="\t", index=False, header=True) 
    print("File product_list_%s.txt written to disk." % max_date)


# In[18]:

    sc.stop()
