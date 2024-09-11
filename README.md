# Online Multiple Hypothesis Testing

[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/OliverHennhoefer/online-fdr/issues)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code_style-black-black)](https://github.com/psf/black)
[![start with why](https://img.shields.io/badge/start%20with-why%3F-brightgreen.svg?style=flat)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7615519/)

The vast majority of implementations of online method for FDR control are either part of an experimental setup, that does
not straight-forwardly generalize towards applications outside this setup, or are geared towards tests for which all test
results are already available (i.e. they do not have an actual _online_ API).

For that reason, this repository implements a wide range of methods for FDR/FWER control for _actual_ online multiple
hypothesis testing with an intuitive `test_one()` method:

- **Alpha Spending** (Bonferroni, ...)
- [**Online Fallback**](https://journals.sagepub.com/doi/abs/10.1177/0962280220983381)
- **[[Generalized] Alpha Investing](https://www.jstor.org/stable/24774568)** ([Foster/Stine](http://deanfoster.net/research/edc.pdf), ...)
- [**LOND**](https://proceedings.neurips.cc/paper/2017/file/7f018eb7b301a66658931cb8a93fd6e8-Paper.pdf) (Original, Modified, Dependent)
- [**LORD**](https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.full) (LORD3, LOND++, D-LORD, Dependent, [DecayLORD](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf))
- [**SAFFRON**](https://proceedings.mlr.press/v80/ramdas18a/ramdas18a.pdf) (Standard, [DecaySAFFRON](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf))
- [**ADDIS**](https://proceedings.neurips.cc/paper_files/paper/2019/file/1d6408264d31d453d556c60fe7d0459e-Paper.pdf) (Standard, [DecayADDIS](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf))
- [**Batch-BH**](https://proceedings.mlr.press/v108/zrnic20a/zrnic20a.pdf) and [**Batch-StBH**](https://proceedings.mlr.press/v108/zrnic20a/zrnic20a.pdf)

_This work is inspired by the R package '[onlineFDR](https://dsrobertson.github.io/onlineFDR/)'. 
This package, and most of its methods, are largely validated by the [implementations](https://github.com/dsrobertson/onlineFDR) of said package.
Key differentiator is the design choice in regard to method calls for sequential testing, as this package allows for truly temporal applications ('onlineFDR' requires a [static] data.frame for testing)._
