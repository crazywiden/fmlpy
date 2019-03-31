require(lubridate)
library(fmlr)
require(optparse)
options(digits.secs=3)

preprocess <- function(raw_data){
  # raw_data is a data.frame
  names(raw_data) <- c("Time", "Type", "OrderID", "Size", "Price", "Direction")
  raw_data$Size <- as.numeric(raw_data$Size)
  raw_data$Price <- as.numeric(raw_data$Price)
  demodate <- "2012-06-21"
  raw_data$time <- as_datetime(demodate, tz="US/Eastern") + raw_data$Time
  data_exc <- subset(raw_data, Type %in% c(4,5)) ## data with transactions
  return(data_exc)
}



option_list = list(
  make_option(c("--time_window"), type="character", default="3s", 
              help="for time bar", metavar="character"),
  make_option(c("--out"), type="character", default="out.txt", 
              help="", metavar="character")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

data_path <- "D:\\fmlpy\\tests\\test_data.csv"
raw_data <- read.csv(data_path,header = F)
useful_data <- preprocess(raw_data)
time_window <- as.numeric(substr(opt$time_window,1,nchar(opt$time_window)-1))
time_bar <- fmlr::bar_time(useful_data,tDur=time_window)
time_bar <- do.call(cbind.data.frame,time_bar)
write.csv(time_bar,file = "D:\\fmlpy_utili\\time_bar.csv")