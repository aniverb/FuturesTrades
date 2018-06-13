setwd("C:\\Users\\aniverb\\Documents\\Grad_School\\JHU\\700")
tv=read.table("trades_pivot_2016-11-18.txt", sep="\t", header=T) 
pv=read.table("trades_pivot_vol_2016-11-18.txt", sep="\t", header = T)
trade_data=read.table("trades_count_regression_2016-11-18.txt", sep="\t", header=T)
tv_pv_comb=cbind(tv[,1:16], pv[,4:16], tv[17], pv[17])
tv_pv_comb["Day"]=trade_data["Day"]
#head(tv_pv_comb)

products=list(c('ZQ', "2016-08-31"), c('YM', '2017-03-17'), c('HO', "2016-11-30"), c('ZF', '2016-12-30'), c('RB', '2016-07-29')) #c('NQ', "2016-12-16"), c('ZC', '2016-07-14')
for (product in products){
  tv_pv_combS=subset(tv_pv_comb, ProductName==product[1])
  tv_pv_combM=subset(tv_pv_combS, Maturity==product[2])
  tradeQuant=quantile(tv_pv_combM$DayTradeTotal, c(.6, .9)) #for trim
  #tv_pv_combM=tv_pv_combM[(tv_pv_combM$DayTradeTotal>tradeQuant[1]) & (tv_pv_combM$DayTradeTotal<tradeQuant[2]),] #for trim
  png(paste(product[1], "tradevolumeTrim.png", sep=""), width = 6, height = 4, units = 'in', res = 300)
  plot(tv_pv_combM$Day, tv_pv_combM$DayTradeTotal, xlab="Day", ylab="DayTradeTotal", main=paste(product[1], "Maturity:", product[2]), col="skyblue", ylim=c(0, max(tv_pv_combM$DayTradeTotal)), pch=16, xaxt="n")
  at=seq(min(tv_pv_combM$Day), max(tv_pv_combM$Day), 1)
  labs=rep(NA, length(at))
  labs[which(at%in%tv_pv_combM$Day)]=as.vector(tv_pv_combM$Date)
  axis(1, at=at, labels=labs, tick=F)
  abline(h=tradeQuant[1], lty=2)
  abline(h=tradeQuant[2], lty=2)
  dev.off()
  #don't run when making trimed plots
  # cors=apply(tv_pv_combM, 1, function(x){cor(as.numeric(x[4:16]), as.numeric(x[17:29]), use="na.or.complete")})
  # tv_pv_combM=data.frame(tv_pv_combM[c("Date", "Day", "DayTradeTotal")], cors=as.vector(cors))
  # #png(paste(product[1], "cor_plot.png", sep=""), width = 6, height = 4, units = 'in', res = 300)
  # plot(tv_pv_combM$Day, tv_pv_combM$cors, ylim=c(-1,1), xlab="Day", ylab="correlation coefficient", main=paste(product[1], "Maturity:", product[2]), xaxt="n")
  # axis(1, at=at, labels=labs, tick=F)
  #dev.off()
}

