import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(dirname(os.getcwd()))))
from fmlpy.preprocess import frac_diff
import subprocess
import argparse
import pandas as pd
import numpy as np 

def parser_args():
    descrip = "fractional differentiation check"
    parser = argparse.ArgumentParser(description=descrip)
    parser.add_argument("--d", type=float, default=0.5, \
        help="fraction difference order")
    parser.add_argument("--N", type=int, default=20, \
        help="number of weights")
    parser.add_argument("--thres", type=float, default=0.0001, \
        help="when to stop for smallest weights")
    return parser.parse_args()


def main(root_path):
    # args = parse_args()
    test_data = pd.read_csv(os.path.join(root_path,"bar_test_data.csv"))
    price = test_data["Price"]
    diff_run_N = frac_diff.frac_diff(price, n_weight=args.N)
    Rmd_N = "Rscript gen_frac_diff.R --d %f --N %d" % (args.d, args.N)
    subprocess.check_output(Rmd_N, universal_newlines=True)
    vec_N = pd.read_csv(os.path.join(root_path,"frac_diff_N.csv"))
    res_N = np.array_equal(diff_run_N,vec_N)

    diff_run_thres = frac_diff.frac_diff(price, thres=args.thres)
    Rmd_thres = "Rscript gen_frac_diff.R --d %f --thres %f" % (args.d, args.thres)
    subprocess.check_output(Rmd_thres, universal_newlines=True)
    vec_thres = pd.read_csv(os.path.join(root_path,"frac_diff_thres.csv"))
    res_thres = np.array_equal(diff_run_thres,vec_thres)

    if not res_N:
        print("##########################################################")
        print("#Something wrong in the calculation of number of weights!#")
        print("##########################################################")

    if not res_thres:
        print("#######################################################")
        print("#Something wrong in the calculation of threshold of w!#")
        print("#######################################################")

    if res_N and res_thres:
        print("################################")
        print("#Awesome! your code is perfect!#")
        print("################################")
    
if __name__ == '__main__':
    root_path = os.getcwd()
    main(root_path)