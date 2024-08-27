# Note:
# Added for clarity regarding LORD test and implementation.
# The current C++ implementation in the R package 'onlineFDR' seems faulty.
# The original R version implemented in 'onlineFDR' seems to be correct.
#
# See Commit:
# https://github.com/dsrobertson/onlineFDR/commit/cefcdad4f3fa7b78def9ff2feda401391ba0d963#diff-a801e455839ea3a17ba9843d9433ce2b16cfe157d52adada2017a3eea19d5140


df <- data.frame(
  id = c('A15432', 'B90969', 'C18705', 'B49731', 'E99902',
         'C38292', 'A30619', 'D46627', 'E29198', 'A41418',
         'D51456', 'C88669', 'E03673', 'A63155', 'B66033'),
  date = as.Date(c(rep("2014-12-01", 3),
                   rep("2015-09-21", 5),
                   rep("2016-05-19", 2),
                   "2016-11-12",
                   rep("2017-03-27", 4))),
  pval = c(2.90e-14, 0.00143, 0.06514, 0.00174, 0.00171,
           3.61e-05, 0.79149, 0.27201, 0.28295, 7.59e-08,
           0.69274, 0.30443, 0.000487, 0.72342, 0.54757),
  decision.times = seq_len(15) + 1,
  lags = rep(1, 15))

LORD <- function(d, alpha=0.05, gammai, version=3, w0=alpha/10, b0=alpha-w0,
                 random=TRUE, date.format="%Y-%m-%d") {
  
  if(length(d$id) == 0){
    stop("The dataframe d is missing a column 'id' of identifiers.")
  } else if(length(d$pval) == 0){
    stop("The dataframe d is missing a column 'pval' of p-values.")
  }
  
  if(length(d$date) == 0){
    warning("No column of dates is provided, so p-values are treated
        as being ordered sequentially with no batches.")
    random = FALSE
  } else if(any(is.na(as.Date(d$date, date.format)))){
    stop("One or more dates are not in the correct format.")
  } else {
    d <- d[order(as.Date(d$date, format = date.format)),]
  }
  
  if(alpha<=0 || alpha>1 ){
    stop("alpha must be between 0 and 1.")
  }
  
  if(!(version %in% 1:3)){
    stop("version must be 1, 2 or 3.")
  }
  
  if(anyNA(d$pval)){
    warning("Missing p-values were ignored.")
    d <- na.omit(d)
  }
  
  if(!(is.numeric(d$pval))){
    stop("The column of p-values contains at least one non-numeric
        element.")
  } else if(any(d$pval>1 | d$pval<0)){
    stop("All p-values must be between 0 and 1.")
  }
  
  N <- length(d$pval)
  
  if(missing(gammai)){
    gammai <- 0.07720838*log(pmax(1:N,2))/((1:N)*exp(sqrt(log(1:N))))
  } else if (any(gammai<0)){
    stop("All elements of gammai must be non-negative.")
  } else if(sum(gammai)>1){
    stop("The sum of the elements of gammai must not be greater than 1.")
  }
  
  if(w0 < 0){
    stop("w0 must be non-negative.")
  } else if(b0 <= 0){
    stop("b0 must be positive.")
  } else if(w0+b0 > alpha & !(isTRUE(all.equal(w0+b0, alpha)))){
    stop("The sum of w0 and b0 must not be greater than alpha.")
  }
  
  if(random){
    Nbatch <- length(unique(d$date))
    set.seed(1)
    
    for(i in 1:Nbatch){
      d.temp <- d[d$date == unique(d$date)[i],]
      d.temp <- d.temp[sample.int(length(d.temp$date)),]
      d[d$date == unique(d$date)[i],] <- d.temp
    }
  }
  
  alphai <- R <- rep(0, N)
  pval <- d$pval
  
  switch(version,
         ## 1
         {
           R <- rep(0, N)
           
           for (i in 1:N){
             tau <- max(0, which(R[1:(i-1)] == 1))
             alphai[i] <- gammai[i]*w0*(tau == 0) + gammai[i-tau]*b0*(tau > 0)
             R[i] <- pval[i] <= alphai[i]
           }
         },
         ## 2
         {
           R <- rep(0, N)
           alphai[1] <- gammai[1]*w0
           R[1] <- pval[1] <= alphai[1]
           
           for (i in 2:N){
             alphai[i] <- gammai[i]*w0 + sum(gammai[i-which(R[1:(i-1)] == 1)])*b0
             R[i] <- pval[i] <= alphai[i]
           }
         },
         ## 3
         {
           R <- W <- rep(0, N+1)
           R[1] <- 1
           W[1] <- w0
           
           alphai[1] <- phi <- gammai[1]*w0
           R[2] <- pval[1] <= alphai[1]
           W[2] <- w0 - phi + R[2]*b0
           
           for (i in 2:N){
             tau <- max(which(R[1:i] == 1))
             alphai[i] <- phi <- gammai[i-tau+1]*W[tau]
             
             R[i+1] <- pval[i] <= alphai[i]
             W[i+1] <- W[i] - phi + R[i+1]*b0
           }
           R <- R[2:(N+1)]
         })
  
  d.out <- data.frame(d, alphai, R)
  
  return(d.out)
}

# LORD 1 (not implemented)
# round(LORD(d=df, alpha=0.05, version=1, w0=0.025, b0=0.025, random=FALSE)[c('alphai', 'R')], digits = 6)
# LORD 2 (not implemented)
# round(LORD(d=df, alpha=0.05, version=2, w0=0.025, b0=0.025, random=FALSE)[c('alphai', 'R')], digits = 6)
# LORD 3 (implemented)
round(LORD(d=df, alpha=0.05, version=3, w0=0.025, b0=0.025, random=FALSE)[c('alphai', 'R')], digits = 6)
