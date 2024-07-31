library(onlineFDR)

set.seed(1)

# Example data.frame

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
  lags = rep(1,15))

#_______________________________________________________________________________
# 0 Alpha Spending (Bonferroni)

alpha <- 0.05
gammai <- rep(alpha/15, 15)
onlineFDR::Alpha_spending(df['pval'], alpha = alpha, gammai = gammai)

#_______________________________________________________________________________
# 1 Alpha Spending (Default)

onlineFDR::Alpha_spending(df['pval'], alpha = 0.05, random = FALSE)

#_______________________________________________________________________________
# 2 Alpha Investing

onlineFDR::Alpha_investing(df, alpha = 0.1, w0 = 0.05, random = FALSE)

#_______________________________________________________________________________
# 3 ADDIS (FDR control)

onlineFDR::ADDIS(df, alpha = 0.1, w0 = 0.05, lambda = 0.25, tau = 0.5,
                 async = FALSE, random = FALSE)

#_______________________________________________________________________________
# 4 ADDIS (FWER control)

onlineFDR::ADDIS_spending(df, alpha = 0.1, lambda = 0.25, tau = 0.5,
                          dep = FALSE)

#_______________________________________________________________________________
# 5 LOND (Original)

onlineFDR::LOND(df, alpha = 0.1, dep = FALSE, random = FALSE)

#_______________________________________________________________________________
# 6 LOND (Modified)

onlineFDR::LOND(df, alpha = 0.1, dep = FALSE, random = FALSE, original = FALSE)

#_______________________________________________________________________________
# 7 LOND* (Async)

onlineFDR::LONDstar(df, alpha = 0.1, version = 'async')

#_______________________________________________________________________________
# 8 LOND* (Dependent)

onlineFDR::LONDstar(df, alpha = 0.1, version = 'dep')

#_______________________________________________________________________________
# 9 LORD++

onlineFDR::LORD(df, alpha = 0.05, version = '++', w0 = 0.01, b0 = 0.04,
                random = FALSE)

#_______________________________________________________________________________
# 10 LORD (Dependent)

onlineFDR::LORD(df, alpha = 0.05, version = 'dep', w0 = 0.01, b0 = 0.04,
                random = FALSE)

#_______________________________________________________________________________
# 11 LORD (Discard)

onlineFDR::LORD(df, alpha = 0.05, version = 'discard', w0 = 0.01, b0 = 0.04,
                tau.discard = 0.5, random = FALSE)

#_______________________________________________________________________________
# 12 SAFFRON

onlineFDR::SAFFRON(df, alpha = 0.1, w0 = 0.05, random = FALSE)

#_______________________________________________________________________________
# 13 SAFFRON* (Async)

onlineFDR::SAFFRONstar(df, alpha = 0.1, version = 'async', w0=0.05,
                       lambda = 0.5)

#_______________________________________________________________________________
# 14 SAFFRON* (Dependent)

onlineFDR::SAFFRONstar(df, alpha = 0.1, version = 'dep', w0=0.05, lambda = 0.5)

#_______________________________________________________________________________
# 15 SAFFRON* (Batch)

onlineFDR::SAFFRONstar(df, alpha = 0.1, version = 'batch', w0=0.05,
                       lambda = 0.5, batch.sizes = nrow(df))
