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
  make_option(c("--bars"), type="character",
              help="time_bar/vol_bar/dollar_bar/VIB/TIB/TRB/VRB", metavar="character"),
  make_option(c("--time_window"), type="character", default="3s",
              help="for time bar", metavar="character"),
  make_option(c("--size"), type="integer", default=1000,
              help="for vol bar/dollar_bar", metavar="character"),
  make_option(c("--ET_window"), type="integer", default=5,
              help="for VIB/TIB/TRB/VRB", metavar="character"),
  make_option(c("--P_window"), type="integer", default=3,
              help="for VIB/TIB", metavar="character"),
  make_option(c("--bt1_window"),type="integer", default=300,
              help = "for TRB/VRB", metavar="character"),
  make_option(c("--pos_vol_window"),type = "integer",default = 400,
              help="for VRB", metavar="character"),
  make_option(c("--neg_vol_window"),type="integer",default=400,
              help = "for VRB", metavar="character"),
  make_option(c("--warm_up_len"), type="integer", default=100,
              help="for VIB/TIB", metavar="character")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)
root_path <- getwd()
data_path <- paste(root_path,"bar_test_data.csv",sep = "/")
raw_data <- read.csv(data_path,header = T)
useful_data <- preprocess(raw_data)

if(opt$bars == "time_bar"){
  time_window <- as.numeric(substr(opt$time_window,1,nchar(opt$time_window)-1))
  time_bar <- fmlr::bar_time(useful_data,tDur=time_window)
  time_bar <- do.call(cbind.data.frame,time_bar)
  write.csv(time_bar,file = paste(root_path,"time_bar.csv",sep = "/"))  
}else if(opt$bars == "vol_bar"){
  vol_bar <- fmlr::bar_volume(useful_data,vol=opt$size)
  vol_bar <- do.call(cbind.data.frame,vol_bar)
  write.csv(vol_bar,file = paste(root_path,"vol_bar.csv",sep = "/"))
}else if(opt$bars == "dollar_bar"){
  dollar_bar <- fmlr::bar_unit(useful_data,unit=opt$size)
  dollar_bar <- do.call(cbind.data.frame,dollar_bar)
  write.csv(dollar_bar,file = paste(root_path,"dollar_bar.csv",sep = "/"))
}else if(opt$bars == "TIB"){
  TIB <- fmlr::bar_tick_imbalance(useful_data, w0=opt$warm_up_len,
                                    bkw_T=opt$ET_window, bkw_b=opt$P_window)
  TIB <- do.call(cbind.data.frame,TIB)
  write.csv(TIB,file = paste(root_path,"TIB.csv",sep = "/"))
}else if(opt$bars == "VIB"){
  VIB <- fmlr::bar_volume_imbalance(useful_data, w0=opt$warm_up_len,
                                  bkw_T=opt$ET_window, bkw_b=opt$P_window)
  VIB <- do.call(cbind.data.frame,VIB)
  write.csv(VIB,file = paste(root_path,"VIB.csv",sep = "/"))
}else if(opt$bars == "TRB"){
  TRB <- fmlr::bar_tick_runs(useful_data, w0=opt$warm_up_len,
                             bkw_T=opt$ET_window,bkw_Pb1=opt$bt1_window)
  TRB <- do.call(cbind.data.frame,TRB)
  write.csv(TRB,file = paste(root_path,"TRB.csv",sep = "/"))
}else if(opt$bars == "VRB"){
  VRB <- fmlr::bar_volume_runs(useful_data, w0=opt$warm_up_len,
                             bkw_T=opt$ET_window, bkw_Pb1=opt$bt1_window,
                             bkw_V=opt$pos_vol_window)
  VRB <- do.call(cbind.data.frame,VRB)
  write.csv(VRB,file = paste(root_path,"TRB.csv",sep = "/"))
}else{
  stop("wrong bars type")
}



