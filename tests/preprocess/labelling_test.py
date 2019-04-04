import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(dirname(os.getcwd()))))
from fmlpy.preprocess import filters
from fmlpy.preprocess import labelling
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
    parser.add_argument("--is_vertical", default="T",\
        choices=["TRUE", "FALSE","True","False","T","F"],\
        help="whether consider vertical bar or not")
    return parser.parse_args()


def main(root_path):
    # read data
    test_data = pd.read_csv(os.path.join(root_path,"bar_test_data.csv"))
    price = test_data["Price"].values

    # prepare for parameters
    args = parser_args()
    thres = args.target
    profit_take = args.pt
    stop_loss = args.sl
    target = args.target
    hold_time = args.hold
    is_vertical = args.is_vertical

    CUMSUM_idx = filters.CUMSUM_filter(price, thres)
    N = len(CUMSUM_idx)
    events = pd.DataFrame({"start_t":CUMSUM_idx + 1, "end_t": CUMSUM_idx + hold_time,\
        "target_rtn":np.repeat(target,N), "side": np.repeat(0,N)})
    meta_label = labelling.meta_label(price, events, profit_take, stop_loss, is_vertical)
    
    Rmd = "Rscript gen_labelling.R --pt %f --sl %f --thres %d --target %f --hold %d --is_vertical %s"\
     % (profit_take, stop_loss, thres, target, hold_time, is_vertical)
    subprocess.check_output(Rmd, universal_newlines=True)
    meta_label_run = pd.read_csv(os.path.join(root_path,"meta_label_run.csv"))
    meta_label_run = meta_label_run[["t0Fea","t1Fea","tLabel","ret","label"]]
    res = meta_label_run.equals(meta_label)
    
    if res:
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