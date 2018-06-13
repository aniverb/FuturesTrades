df=data.frame(Products=c("HO", "6E", "CL", "ES", "KE", "ZL", "CL", "GC", "RB", "GE", "GE", "GE", "UB", "ZB", "ZM", "ZQ"),  Maturities=c("2016-09-30","2017-06-19", "2016-07-20", "2016-09-16", "2016-12-14","2016-12-14", "2017-01-20", "2016-10-27", "2016-17-29", "2016-09-19", "2016-07-18", "2016-11-14", "2016-09-21", "2016-09-21", "2016-10-14", "2016-07-29"))

inDF=function(x, product, maturity){
  if ((x[1]==product) & (x[2]==maturity)){
    return(TRUE)
  }else{
    return(FALSE)
  }
}

t=apply(df, 1, inDF, "ZQ", "2016-08-31")
T %in% t
