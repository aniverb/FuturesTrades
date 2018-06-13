setwd("your\computer\directory")	
tv=read.table("trades_pivot_2016-11-18.txt", sep="\t", header=T) 	
pv=read.table("trades_pivot_vol_2016-11-18.txt", sep="\t", header = T)	
trade_data=read.table("trades_count_regression_2016-11-18.txt", sep="\t", header=T)	
tv_pv_comb=cbind(tv[,1:16], pv[,4:16], tv[17], pv[17])	
tv_pv_comb["Day"]=trade_data["Day"]	
head(tv_pv_comb)	
	
pvals=c()	
prod=c()	
products=as.vector(unique(tv_pv_comb$ProductName))	
significant=list(c("ZQ", "2016-08-31"), c("YM", "2017-03-17"), c("HO", "2016-11-30"), c("ZF", "2016-12-30"), c("RB", "2016-07-29"))	
dfInt=data.frame(Products=c("HO", "6E", "CL", "ES", "KE", "ZL", "CL", "GC", "RB", "GE", "GE", "GE", "UB", "ZB", "ZM", "ZQ"),  Maturities=c("2016-09-30","2017-06-19", "2016-07-20", "2016-09-16", "2016-12-14","2016-12-14", "2017-01-20", "2016-10-27", "2016-07-29", "2016-09-19", "2016-07-18", "2016-11-14", "2016-09-21", "2016-09-21", "2016-10-14", "2016-07-29"))	
	
inDF=function(x, product, maturity){	
  if ((x[1]==product) & (x[2]==maturity)){	
    return(TRUE)	
  }else{	
    return(FALSE)	
  }	
}	
	
for (product in products){ #in results, put 3 plots on 1 line	
  tv_pv_combS=subset(tv_pv_comb, ProductName==product)	
  maturities=as.vector(unique(tv_pv_combS$Maturity))	
  for (maturity in maturities){	
    tv_pv_combM=subset(tv_pv_combS, Maturity==maturity)	
      if (nrow(tv_pv_combM)>=30){	
        cors=apply(tv_pv_combM, 1, function(x){cor(as.numeric(x[4:16]), as.numeric(x[17:29]), use="na.or.complete")})	
        dfCors=data.frame(tv_pv_combM[c("Date", "Day", "DayTradeTotal")], cors=as.vector(cors))	
        tradeQuant=quantile(dfCors$DayTradeTotal, c(.6, .9)) 	
        tv_pv_combMQ=dfCors[(dfCors$DayTradeTotal>tradeQuant[1]) & (dfCors$DayTradeTotal<tradeQuant[2]),] #selecting high volume trades	
        mod=lm(tv_pv_combMQ$cors~tv_pv_combMQ$Day) 	
        cor_hat=predict(mod, tv_pv_combMQ["Day"])	
        tv_pv_combMQ["cor_hat"]=cor_hat	
        	
        #saving correlation plots of significance with line of best fit
        if ((product==significant[[1]][1]) & (maturity==significant[[1]][2]) | (product==significant[[2]][1]) & (maturity==significant[[2]][2]) | (product==significant[[3]][1]) & (maturity==significant[[3]][2])| (product==significant[[4]][1]) & (maturity==significant[[4]][2])| (product==significant[[5]][1]) & (maturity==significant[[5]][2])){
          png(paste("Coeff_fit", product, maturity, ".png", sep=""), width = 7, height = 7, units = 'in', res = 400)
          plot(tv_pv_combMQ$Day, tv_pv_combMQ$cors, ylim=c(-1,1), xlab="Day", ylab="correlation coefficient", main=paste(product, "Maturity:", maturity), xaxt="n")
          lines(tv_pv_combMQ$Day, tv_pv_combMQ$cor_hat, col="red")
          at=seq(min(tv_pv_combMQ$Day), max(tv_pv_combMQ$Day), 1)
          labs=rep(NA, length(at))
          labs[which(at%in%tv_pv_combMQ$Day)]=as.vector(tv_pv_combMQ$Date)
          axis(1, at=at, labels=labs, tick=F)
          dev.off()
        }
        	
        plot(tv_pv_combMQ$Day, tv_pv_combMQ$cors, ylim=c(-1,1), xlab="Day", ylab="correlation coefficient", main=paste(product, "Maturity:", maturity), xaxt="n")  	
        lines(tv_pv_combMQ$Day, tv_pv_combMQ$cor_hat, col="red")	
        at=seq(min(tv_pv_combMQ$Day), max(tv_pv_combMQ$Day), 1)	
        labs=rep(NA, length(at))	
        labs[which(at%in%tv_pv_combMQ$Day)]=as.vector(tv_pv_combMQ$Date)	
        axis(1, at=at, labels=labs, tick=F)	
        	
        stat=summary(mod)	
        stat=summary(mod)	
        cof=stat$coefficients	
        pval=cof[,4][2]	
        pvals=append(pvals, pval, after=length(pvals))	
        prod=append(prod, paste(product, maturity), after=length(prod))	
        	
        trades=as.vector(as.matrix(t(tv_pv_combM[,4:16])))	
        priceVol=as.vector(as.matrix(t(tv_pv_combM[,17:29])))	
        df=data.frame(trades, priceVol)[order(trades),]	
        df=na.omit(df)	
        n=nrow(df)	
        dfTrim=df[ceiling(.05*n):round(.95*n),]	
        dfTrimO=dfTrim[order(dfTrim$priceVol),]	
        n2=nrow(dfTrimO)	
        dfTrimP=dfTrimO[ceiling(.05*n2):round(.95*n2),]	
        	
        plot(dfTrimP, xlab="trade volume hourly", ylab="price volatility hourly", main=paste(product, "Maturity:", maturity), pch=20) 	
        	
        daily=tv_pv_combM[,30:31][order(tv_pv_combM$DayTradeTotal),]	
        daily=na.omit(daily)	
        nD=nrow(daily)	
        dailyTrim=daily[ceiling(.05*nD):round(.95*nD),]	
        dailyTrimO=dailyTrim[order(dailyTrim$DayVolatility),]	
        nD2=nrow(dailyTrimO)	
        dailyTrimP=dailyTrimO[ceiling(.05*nD2):round(.95*nD2),]	
        plot(dailyTrimP, xlab="trade volume daily", ylab="price volatility daily", main=paste(product, "Maturity:", maturity), pch=20)	
        	
        t=apply(dfInt, 1, inDF, product, maturity)	
        if (TRUE %in% t){	
          png(paste(product, maturity, "hourly.png", sep=""), width = 6, height = 4, units = 'in', res = 300)	
          plot(dfTrimP, xlab="trade volume hourly", ylab="price volatility hourly", main=paste(product, "Maturity:", maturity), col="pink3", pch=20)	
          dev.off()	
          png(paste(product, maturity, "daily.png", sep=""), width = 6, height = 4, units = 'in', res = 300)	
          plot(dailyTrimP, xlab="trade volume daily", ylab="price volatility daily", main=paste(product, "Maturity:", maturity), col="pink3", pch=20)	
          dev.off()	
        }	
    }	
  }	
}	
	
pvalsO=order(pvals)	
corPvals=data.frame(prod, pvals)[pvalsO,]	
nPvals=nrow(corPvals)	
nPvals	
corPvals["id"]=1:nPvals #B-H Procedure	
corPvals["q"]=nPvals*corPvals$pvals/corPvals$id	
f=c()	
for(i in 1:nPvals){f=append(f, min(corPvals$q[i:nPvals]), length(f))}	
corPvals["f"]=f	
corSig=corPvals[which(corPvals$pvals<.05),]	
nSig=nrow(corSig)	
nSig	
corSig #4 rejected at FDR=.20 	

#uniform Q-Q plot
set.seed(3-3-17)	
u=sort(runif(length(pvals)))	
#png("unifQQ.png")	
plot(u, corPvals$pvals, ylab="p-values", xlab="uniform", main="Q-Q Plot")	
abline(0,1, col="red")	
#dev.off()	
