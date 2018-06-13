library(mgcv)
library(ggplot2)

setwd("C:/Users/aniverb/Documents/Grad_School/JHU/700")
trade_data=read.table("trades_count_regression_2016-11-18.txt", header=T)
head(trade_data)

#use only half of data
n=dim(trade_data)[1]/2
reg_data=trade_data[1:n, ]

set.seed(12-1-16)
train_id=sample(1:n, n)[1:floor(n/2)]
train=reg_data[train_id, ]
test=reg_data[-train_id, ]

model1 <- gam(TradeTotBCTrans ~ s(TimeToMaturity, bs="cr") + s(DayofMonth, bs="cr") + s(Day, bs="cr") + factor(ProductType) + factor(ProductName) + factor(DayOfTheWeek), family=gaussian(), data = train, method="GCV.Cp", select=TRUE)
summary(model1)
plot(model1)
model1$coefficients
model1$sp
res=model1$residuals
trainPred=model1$fitted.values
plot(train$TradeTotBCTrans, col="red")
points(trainPred)

predictM2 <- predict(model1, test)
                     
#with day of month factored instead of splined(ceates a lot of addtl vars)
model2 <- gam(TradeTotBCTrans ~ s(TimeToMaturity, bs="cr") + s(Day, bs="cr") + factor(ProductType) + factor(ProductName) + factor(DayOfTheWeek) + factor(DayofMonth), family=gaussian(), data = train, method="GCV.Cp", select=TRUE)
summary(model2) #not significantly better than model 1
plot(model2)

predictM2 <- predict(model, type="lpmatrix")

