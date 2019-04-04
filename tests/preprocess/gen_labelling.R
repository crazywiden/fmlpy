library(lubridate)
library(fmlr)
library(optparse)
library(anytime)
rm(list=ls())
options(digits.secs=3)

preprocess <- function(raw_data){
  # raw_data is a data.frame
  names(raw_data) <- c("time", "Price","Size")
  raw_data$time <- anytime(raw_data$time)
  raw_data$Size <- as.numeric(raw_data$Size)
  raw_data$Price <- as.numeric(raw_data$Price)
  return(raw_data)
}

option_list = list(
  make_option(c("--pt"), type="double",default=1,
              help="profit taking", metavar="character"),
  make_option(c("--sl"), type="double", default=1,
              help="stop loss", metavar="character"),
  make_option(c("--thres"), type="integer", default=1000,
              help="threshold for CUMSUM filter", metavar="character"),
  make_option(c("--target"), type="double", default=0.005,
              help="minimum return of each label(we assume symmetric)", 
              metavar="character"),
  make_option(c("--hold"), type="integer", default=200,
              help="maximum holding time", metavar = "character"),
  make_option(c("--is_vertical"), type="character", default="T",
              help="whether consider vertical bar or not", metavar = "character")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)
root_path <- getwd()
# root_path <- "D://fmlpy//tests//preprocess"
data_path <- paste(root_path,"bar_test_data.csv",sep = "/")
raw_data <- read.csv(data_path,header = T)
raw_data <- preprocess(raw_data)

thres <- opt$thres
hold_T <- opt$hold
target <- opt$target
profit_taking <- opt$pt
stop_loss <- opt$sl
vert <- opt$is_vertical
if(vert %in% c("T","True","TRUE")){
  is_vert <- TRUE
}else if(vert %in% c("F","False", "FALSE")){
  is_vert <- FALSE
}else{
  stop("please enter proper value: T/True/TRUE/F/False/FALSE")
}

price <- raw_data$Price
CUMSUM_idx <- fmlr::istar_CUSUM(price,thres)
n_event <- length(CUMSUM_idx)
# 
# # side[i] == 0 means take both profit taking and stop loss at time i
# # side[i] == 1 means only take profit taking 
# # side[i] == -1 means only take stop loss
events <- data.frame(t0=CUMSUM_idx+1, t1=CUMSUM_idx+hold_T, trgt=rep(target, n_event), side=rep(0, n_event))

ptSl <- c(profit_taking, stop_loss)
out <- fmlr::label_meta(price, events, ptSl, ex_vert = is_vert)
write.csv(out,file=paste(root_path,"meta_label_run.csv",sep="/"))


