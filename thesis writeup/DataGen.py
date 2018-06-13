#Jupyter Notebook Code: NOT MEANT TO BE EXECUTABLE

import numpy as np
import pandas as pd
from scipy import stats
from pyspark import SparkContext, SparkConf
from pyspark.sql import DataFrame, HiveContext #SQLContext 
from pyspark.sql.functions import *
from pyspark.sql.types import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

sconf = SparkConf().setMaster("local[32]").setAppName("TradeDataCount").set("spark.driver.maxResultSize", "32g").set("spark.shuffle.consolidateFiles", "true") #spark://10.160.5.48:7077 or local[*] to use as many threads as cores
sc = SparkContext(conf=sconf)
hc = HiveContext (sc)

dataset=sc.pickleFile('raw_dataset_rdd.pickle')
dataset=dataset.toDF()

holidays=["2016-05-30", "2016-07-04", "2016-09-05"] #better to exclude files when doing intial parsing?
data=(dataset
.select(['ProductName', 'Maturity', 'Date', 'TimeStamp', hour("TimeStamp").alias("Hour"), 'Price', 'Quantity'])
.where((dataset.Date.isin(holidays)==False)).cache())
print "Raw data is %d rows." % data.count()

max_date=data.select(max('Date')).first()
print "Max date is %s." % max_date

data.registerTempTable("RawData")
#check holidays and weather index gone
hc.sql('select * from RawData where Date in ("2016-05-30", "2016-07-04", "2016-09-05")').show()

uniqueDates=hc.sql("select distinct Date from RawData order by Date ASC")
uniqueDatesDF=uniqueDates.toPandas()
uniqueDatesDF.head(10)

n=len(uniqueDatesDF)
n

uniqueDatesDF['Day']=range(1, n+1)
uniqueDatesDF.tail(10)

def productConv(product):
    if product in ['6E', 'GE']:
        return 'FX'
    elif product in ['SI', 'GC']: 
        return 'Metal'
    elif product in ['CL', 'NG', 'RB', 'HO']:
        return 'Energy'
    elif product in ['ES', 'NQ', 'YM']:
        return 'Index'
    elif product in ['KE', 'ZC', 'ZL', 'ZM', 'ZW']:
        return 'Agr'
    else:
        return 'Bond'
    
productConvUDF=udf(productConv, StringType())

#changing dates to integer values for ease of graphing via uniqueDatesDF look up table
def dateConv(date):
    if date in list(uniqueDatesDF["Date"]):
        return int(uniqueDatesDF.loc[uniqueDatesDF["Date"]==date]['Day'])
    else:
        return 0
    
dateConvUDF=udf(dateConv, IntegerType())

#Creating the price volatility data set. getting hourly volatility
pivotVol=(data
  .groupBy("ProductName", "Maturity", "Date")     
  .pivot("Hour")
  .agg(round(stddev_samp("Price"), 3))
  .orderBy("ProductName", "Maturity", "Date")       
  .cache())
  
print "Pivoted data is %d rows." % pivotVol.count()

pivotVol.show(5)

#getting daily volatility
dayVol= hc.sql('select ProductName, Maturity, Date, round(stddev_samp(Price), 3) DayVolatility from RawData group by               ProductName, Maturity, Date order by ProductName, Maturity, Date')
dayVol.show(5)

pivotVolDF=pivotVol.toPandas()
dayVolDF=dayVol.toPandas()
pivotVolDF["DayVolatility"]=dayVolDF["DayVolatility"]
pivotVolDF.head()

pivotVolDF.to_csv("trades_pivot_vol_%s.txt" % max_date, sep='\t', index=False)

#Creating the trade volume data set.
pivot=(data
  .groupBy("ProductName", "Maturity", "Date")   
  .pivot("Hour")
  .agg(sum("Quantity"))
  .orderBy("ProductName", "Maturity", "Date")       
  .na.fill(0)
  .cache())
  
print "Pivoted data is %d rows." % pivot.count()

pivot.show(5)

pivotDF=pivot.toPandas()
pivotDF['DayTradeTotal'] = pivotDF[pivotDF.columns[3:]].sum(axis=1)
pivotDF.head()

pivotDF.to_csv("trades_pivot_%s.txt" % max_date, sep='\t', index=False)

#creating regression data set
#adding Time to Maturity, Day of week, Day of Month, Product Type/Market, and Day columns
pivot=pivot.select(["*", datediff(pivot.Maturity, pivot.Date).alias("TimeToMaturity"), date_format(pivot.Date, 'E').alias('DayOfTheWeek'), dayofmonth(pivot.Date).alias('DayofMonth')])
pivot=pivot.withColumn("ProductType", productConvUDF(pivot.ProductName)).withColumn("Day", dateConvUDF(pivot.Date))#.withColumn("DayofWeek", dayConvUDF(pivot.DayOfTheWeek))
pivot.select(["ProductName", "Date", "Day"]).where(pivot.Day==0).show() #check all dates matched, should get null result

pivot.columns

pivot.columns[0:3]+pivot.columns[-5:]

pivotDF=pivot.toPandas()
pivotDF['DayTradeTotal'] = pivotDF[pivotDF.columns[3:-5]].sum(axis=1)
pivotDF.head() 

pivotDF['TradeTotBCTrans']=stats.boxcox(pivotDF['DayTradeTotal'])[0]
pivotDF['TradeTotLogTrans']=np.log(pivotDF['DayTradeTotal'])
dataset=pivotDF[list(pivotDF.columns[0:3])+list(pivotDF.columns[-8:])]
dataset.head()

dataset.to_csv("trades_count_regression_%s.txt" % max_date, sep='\t', index=False)

sc.stop()


