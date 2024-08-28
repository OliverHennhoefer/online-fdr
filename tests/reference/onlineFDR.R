# Documentation:
# https://bioconductor.org/packages/devel/bioc/vignettes/onlineFDR/inst/doc/theory.html

library(onlineFDR)

set.seed(1)

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

# test_addis.py
round(onlineFDR::ADDIS(df$pval, alpha = 0.05, w0 = 0.025, lambda = 0.25, tau = 0.5)[c('alphai', 'R')], digits = 6)

# test_saffron.py
round(onlineFDR::SAFFRON(df$pval, alpha = 0.05, w0 = 0.025, lambda = 0.5)[c('alphai', 'R')], digits = 6)

# test_lord.py
#round(onlineFDR::LORD(df$pval, alpha = 0.05, version = 3, w0 = 0.025, b0 = 0.025)[c('alphai', 'R')], digits = 6)  # compare onlineFDR_lond.R
round(onlineFDR::LORD(df$pval, alpha = 0.05, version = "++", w0 = 0.025, b0 = 0.025, tau.discard = 0.5)[c('alphai', 'R')], digits = 6)
round(onlineFDR::LORD(df$pval, alpha = 0.05, version = "discard", w0 = 0.025, b0 = 0.025, tau.discard = 0.5)[c('alphai', 'R')], digits = 6)

# test_lond.py
round(onlineFDR::LOND(df$pval, alpha = 0.05, original = TRUE, dep = FALSE)[c('alphai', 'R')], digits = 6)
round(onlineFDR::LOND(df$pval, alpha = 0.05, original = TRUE, dep = TRUE)[c('alphai', 'R')], digits = 6)
round(onlineFDR::LOND(df$pval, alpha = 0.05, original = FALSE, dep = FALSE)[c('alphai', 'R')], digits = 6)
round(onlineFDR::LOND(df$pval, alpha = 0.05, original = FALSE, dep = TRUE)[c('alphai', 'R')], digits = 6)

# test_alpha_investing.py
round(onlineFDR::Alpha_investing(df$pval, alpha = 0.05, w0 = 0.025)[c('alphai', 'R')], digits = 6)

# test_alpha_spending.py
round(onlineFDR::Alpha_spending(df$pval, alpha = 0.05)[c('alphai', 'R')], digits = 6)

# test_online_fallback.py
round(onlineFDR::online_fallback(df$pval, alpha = 0.05)[c('alphai', 'R')], digits = 6)