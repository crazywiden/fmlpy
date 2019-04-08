import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(dirname(os.getcwd()))))
from fmlpy.preprocess import filters
from fmlpy.preprocess import feature_mat
import subprocess
import argparse
import pandas as pd
import numpy as np 

def parser_args():
    descrip = "fractional differentiation check"
    parser = argparse.ArgumentParser(description=descrip)
    parser.add_argument("--pt", type=float, default=1,\
        help="profit taking")
    parser.add_argument("--sl", type=float, default=1,\
        help="stop loss")
    parser.add_argument("--thres", type=int, default=200, \
        help="threhold for CUMSUM filter")
    parser.add_argument("--target", type=float, default=0.001, \
        help="minimum return of each label(we assume symmetric)")
    parser.add_argument("--hold", type=int, default=200,\
        help="maximum holding time")
    parser.add_argument("--inclu_vertical", default="False",\
        choices=["TRUE", "FALSE","True","False","T","F","1","0"],\
        help="whether consider vertical bar or not")
    return parser.parse_args()


def main(root_path):
    # read data
    test_data = pd.read_csv(os.path.join(root_path,"bar_test_data.csv"))
    price = test_data["Price"].values

    # prepare for parameters
    args = parser_args()
    thres = args.thres
    profit_take = args.pt
    stop_loss = args.sl
    target = args.target
    hold_time = args.hold
    if args.inclu_vertical in ["FALSE","False","F","0"]:
        inclu_vertical = False
    elif args.inclu_vertical in ["TRUE","True","T","1"]:
        inclu_vertical = True

    CUMSUM_idx = filters.CUMSUM_filter(price, thres)
    N = len(CUMSUM_idx)
    # each element in CUMSUM_idx is the time point when signal appears
    # also because price is all close price, so we can only take action the next minute/day
    # so label should start from CUMSUM_idx + 1
    events = pd.DataFrame({"start_t":CUMSUM_idx + 1, "end_t": CUMSUM_idx + hold_time,\
        "target_rtn":np.repeat(target,N), "side": np.repeat(0,N)})
    meta_label = feature_mat.meta_label(price, events, profit_take, stop_loss, inclu_vertical)
    
    Rmd = "Rscript gen_labelling.R --pt %f --sl %f --thres %d --target %f --hold %d --inclu_vertical %s"\
     % (profit_take, stop_loss, thres, target, hold_time, args.inclu_vertical)
    subprocess.check_output(Rmd, universal_newlines=True)
    meta_label_run = pd.read_csv(os.path.join(root_path,"meta_label_run.csv"))
    meta_label_run = meta_label_run[["t0Fea","t1Fea","tLabel","label","ret"]]
    # to compare index between python and R, we need to transform index in R minus 1
    meta_label_run["t0Fea"] = meta_label_run["t0Fea"] - 1
    meta_label_run["t1Fea"] = meta_label_run["t1Fea"] - 1
    meta_label_run["tLabel"] = meta_label_run["tLabel"] - 1

    # doesn't use DataFrame.equals() because price return in python and R has different precision
    feature_start_diff = len(np.where((meta_label["feature_start"]-meta_label_run["t0Fea"])!=0)[0])
    feature_end_diff = len(np.where((meta_label["feature_end"]-meta_label_run["t1Fea"])!=0)[0])
    label_idx_diff = len(np.where((meta_label["label_point"]-meta_label_run["tLabel"])!=0)[0])
    rtn_diff = len(np.where((meta_label["return"]-meta_label_run["ret"]>1e-9))[0])
    label_diff = len(np.where((meta_label["label"]-meta_label_run["label"])!=0)[0])
    
    diff = [feature_start_diff,feature_end_diff,label_idx_diff,rtn_diff,label_diff]
    if not np.any(diff):
        print("################################")
        print("#Awesome! your code is perfect!#")
        print("################################")
    else:
        print("#####################")
        print("#Oops! bugs detected#")
        print("#####################")
    
if __name__ == '__main__':
    root_path = os.getcwd()
    main(root_path)
