#testing
library(mgcv)
library(ggplot2)
# fake data
n <- 50
sig <- 2
dat <- gamSim(1,n=n,scale=sig)

# select smoothing parameters with REML, using P-splines
b2 <- mgcv::gam(y ~ s(x1, bs='ps') + s(x2, bs='ps') + x3, data = dat, method="REML")
summary(b2)
plot(b2)

# plot the smooth predictor function for x1 with ggplot to get a nicer looking graph
p <- predict(b2, type="lpmatrix")
beta <- coef(b2)[grepl("x1", names(coef(b2)))]
s <- p[,grepl("x1", colnames(p))] %*% beta
ggplot(data=cbind.data.frame(s, dat$x1), aes(x=dat$x1, y=s)) + geom_line()

beta <- coef(b2)[grepl("x2", names(coef(b2)))]
s <- p[,grepl("x2", colnames(p))] %*% beta
ggplot(data=cbind.data.frame(s, dat$x2), aes(x=dat$x2, y=s)) + geom_line()

# select variables and smoothing parameters
b3 <- mgcv::gam(y ~ s(x0, bs="cr") + s(x1, bs="cr") + s(x2, bs="cr") + s(x3, bs="cr") , data = dat, select=TRUE)
summary(b3) #R-sq, Dev exp increases and well scale/sd is very close to actual!
plot(b3)
