library(lubridate)
library(fmlr)
library(optparse)
library(anytime)
rm(list=ls())
options(digits.secs=3)

option_list = list(
  make_option(c("--d"), type="double",default=0.5,
              help="fraction difference order", metavar="character"),
  make_option(c("--thres"), type="double", default=0.0001,
              help="when to stop for smallest weights", metavar="character"),
  make_option(c("--N"), type="integer", default=20,
              help="number of weights", metavar="character")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)
root_path <- getwd()
data_path <- paste(root_path,"bar_test_data.csv",sep = "/")
raw_data <- read.csv(data_path,header = T)
price <- raw_data$Price

# if is.null(tau) == False, then ignore nWei
frac_diff_price_tau <- fmlr::fracDiff(price, d=opt$d, tau=opt$thres)
frac_diff_price_N <- fmlr::fracDiff(price, d=opt$d, nWei=opt$N)
write.csv(frac_diff_price_N,file = paste(root_path,"frac_diff_N.csv",sep = "/"))  
write.csv(frac_diff_price_tau,file = paste(root_path,"frac_diff_thres.csv",sep = "/"))  
