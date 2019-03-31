import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(dirname(os.getcwd()))))
from fmlpy.preprocess import bars
import subprocess
import argparse
import pandas as pd
import numpy as np 

def parser_args():
    descrip = "time bars check"
    parser = argparse.ArgumentParser(description=descrip)
    parser.add_argument("--bars", type=str, help="time_bar/vol_bar/dollar_bar/VIB/TIB/TRB/VRB")
    parser.add_argument("--time_window", type=str, default="3s",\
        help="for time bar")
    parser.add_argument("--size", type=int, default = 10000, \
        help="for vol bar/dollar_bar")
    parser.add_argument("--ET_window", type=int, default=400, \
        help="for VIB/TIB/VRB/TRB")
    parser.add_argument("--P_window", type=int, default=400, \
        help="for VIB/TIB")
    parser.add_argument("--warm_up_len", type=int, default=100, \
        help="for VIB/TIB/VRB/TRB")
    parser.add_argument("--bt1_window", type=int, default=100,\
        help="for VRB/TRB")
    parer.add_argument("--pos_vol_window",type=int,default=100,\
        help="for VRB")
    parser.add_argument("--neg_vol_window",type=int,default=100,\
        help="for VRB")
    return parser.parse_args()

def bar_compare(run_path, test_path):
    """
    compare if two csv files are same
    only compare H/C/L/O but drop the first column
    """
    run_data = pd.read_csv(run_path)
    test_data = pd.read_csv(test_path)
    run_subset = run_data[["close","high","open","low"]]
    test_subset = test_data[["C","H","O","L"]]
    for i in range(run_subset.shape[1]):
        tmp_run = run_subset.iloc[:,i]
        tmp_test = test_subset.iloc[:,i]
        diff = np.where((tmp_run - tmp_test) != 0)
        if len(diff[0]) != 0:
            return False
    return True

def check_time_bar(args,test_data,root_path):
    T_win = args.time_window
    bar_loc = bars.time_bar(test_data,time_window=T_win)
    bar_loc.to_csv(os.path.join(root_path,"time_bar_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars time_bar --time_window " + T_win
    subprocess.check_output(R_cmd, universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"time_bar_run.csv"),\
        os.path.join(root_path,"time_bar.csv"))
    return res

def check_vol_bar(args,test_data,root_path):
    Size = args.size
    bar_loc = bars.volume_bar(test_data,size=Size)
    bar_loc.to_csv(os.path.join(root_path,"vol_bar_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars vol_bar --size " + str(Size)
    subprocess.check_output(R_cmd, universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"vol_bar_run.csv"),\
        os.path.join(root_path,"vol_bar.csv"))
    return res

def check_dollar_bar(args,test_data,root_path):
    Size = args.size
    bar_loc = bars.dollar_bar(test_data,bar=Size)
    bar_loc.to_csv(os.path.join(root_path,"dollar_bar_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars dollar_bar --size " + str(Size)
    subprocess.check_output(R_cmd, universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"dollar_bar_run.csv"),\
        os.path.join(root_path,"dollar_bar.csv"))
    return res

def check_TIB(args,test_data,root_path):
    ET_win = args.ET_window
    P_win = args.P_window
    warm_len = args.warm_up_len
    TIB = bars.imbalance_bar(test_data,ET_win,P_win,warm_len,\
        mode = "TIB")
    TIB.to_csv(os.path.join(root_path,"TIB_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars TIB --ET_window %d --P_window %d --warm_up_len %d" % \
    (ET_win,P_win,warm_len)
    subprocess.check_output(R_cmd,universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"TIB_run.csv"),\
        os.path.join(root_path,"TIB.csv"))
    return res

def check_VIB(args,test_data,root_path):
    ET_win = args.ET_window
    P_win = args.P_window
    warm_len = args.warm_up_len
    VIB = bars.imbalance_bar(test_data,ET_win,P_win,warm_len,\
        mode = "VIB")
    VIB.to_csv(os.path.join(root_path,"VIB_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars VIB --ET_window %d --P_window %d --warm_up_len %d" % \
    (ET_win,P_win,warm_len)
    subprocess.check_output(R_cmd,universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"VIB_run.csv"),\
        os.path.join(root_path,"VIB.csv"))
    return res

def check_TRB(args,test_data,root_path):
    ET_win = args.ET_window
    bt1_win = args.bt1_window
    warm_len = args.warm_up_len
    TRB = bars.tick_run_bar(test_data,ET_win,bt1_win,warm_len)
    TRB.to_csv(os.path.join(root_path,"TRB_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars TRB --ET_window %d --bt1_window %d --warm_up_len %d" % \
    (ET_win, bt1_win, warm_len)
    subprocess.check_output(R_cmd, universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"TRB_run.csv"),\
        os.path.join(root_path,"TRB.csv"))
    return res

def check_VRB(args,test_data,root_path):
    ET_win = args.ET_window
    bt1_win = args.bt1_window
    pos_vol_win = args.pos_vol_window
    neg_vol_win = args.neg_vol_window
    warm_len = args.warm_up_len
    TRB = bars.vol_run_bar(test_data,ET_win,bt1_win,pos_vol_win,neg_vol_win,warm_up_len)
    TRB.to_csv(os.path.join(root_path,"VRB_run.csv"))
    R_cmd = "Rscript gen_bars.R --bars VRB --ET_window %d --bt1_window %d " + \
            "--pos_vol_window %d -- neg_vol_window %d --warm_up_len %d" % \
            (ET_win,bt1_win,pos_vol_win,neg_vol_win,warm_up_len)
    subprocess.check_output(R_cmd, universal_newlines=True)
    res = bar_compare(os.path.join(root_path,"VRB_run.csv"),\
        os.path.join(root_path,"VRB.csv"))
    return res

def main(root_path):
    args = parser_args()
    test_data = pd.read_csv(os.path.join(root_path,"bar_test_data.csv"))
    if args.bars == "time_bar":
        res = check_time_bar(args,test_data,root_path)
    elif args.bars == "dollar_bar":
        res = check_dollar_bar(args,test_data,root_path)
    elif args.bars == "vol_bar":
        res = check_vol_bar(args,test_data,root_path)
    elif args.bars == "VIB":
        res = check_VIB(args,test_data,root_path)
    elif args.bars == "TIB":
        res = check_TIB(args,test_data,root_path)
    elif args.bars == "TRB":
        res = check_TRB(args,test_data,root_path)
    elif args.bars == "VRB":
        res = check_VRB(args,test_data,root_path)
    if res:
        print("################################")
        print("#Awesome! your code is perfect!#")
        print("################################")
    else:
        print("#####################")
        print("#oops! bugs detected#")
        print("#####################")

if __name__ == '__main__':
    root_path = os.getcwd()
    main(root_path)