import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(dirname(os.getcwd()))))
from fmlpy.preprocess import filters
import subprocess
import argparse
import pandas as pd
import numpy as np 


def parser_args():
    descrip = "fractional differentiation check"
    parser = argparse.ArgumentParser(description=descrip)
    parser.add_argument("--thres", type=float, default=10, \
        help="threshold of CUMSUM filter")
    return parser.parse_args()

def main(root_path):
    args = parser_args()

    data = pd.read_csv(os.path.join(root_path,"bar_test_data.csv"))
    price = data["Price"]
    thres = args.thres
    CUMSUM_idx = filters.CUMSUM_filter(price, thres)
    np.savetxt("CUMSUM_idx.csv", CUMSUM_idx, delimiter=",")

    Rmd = "Rscript gen_filters.R --thres %f" % thres
    subprocess.check_output(Rmd, universal_newlines=True)
    CUMSUM_idx_run = pd.read_csv(os.path.join(root_path,"CUMSUM_idx_run.csv"))
    CUMSUM_idx_run = CUMSUM_idx_run["x"].values
    
    # because in python vector start from index 0, so to compare we need plus 1
    res = np.array_equal(CUMSUM_idx+1, CUMSUM_idx_run) 
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
