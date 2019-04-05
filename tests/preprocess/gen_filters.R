library(optparse)
library(fmlr)



opt_list = list(
  make_option(c("--thres"), type="double", default = 200,
              help="threshold of CUMSUM filter", metavar = "character")
)

opt_parser = OptionParser(option_list=opt_list)
opt = parse_args(opt_parser)
# root_path <- "D:\\fmlpy\\tests"
root_path <- getwd()
raw_data <- read.csv(paste(root_path, "bar_test_data.csv",sep="/"))
price <- raw_data$Price

thres = opt$thres
CUMSUM_filter <- fmlr::istar_CUSUM(price, thres)
write.csv(CUMSUM_filter,file=paste(root_path,"CUMSUM_idx_run.csv",sep = "/"))
