import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(dirname(os.getcwd()))))
import fmlpy.preprocess as fpre
import fmlpy.model as fm
import pandas as pd 
import numpy as np 
# load data
root_path = os.getcwd()
test_data = pd.read_csv(os.path.join(root_path,"bar_test_data.csv"))

############################################################
#                 Step 1: Generate Bars                    #  
############################################################
# multiple ways are provided to generate bars
T_win = "10s" 
t_bars = fpre.time_bar(test_data,time_window=T_win)

# Size = 100000
# vol_bars = bars.volume_bar(test_data,size=Size)


# Size = 100000
# d_bars = bars.dollar_bar(test_data,bar=Size)

# ET_win = 400
# P_win = 400
# warm_len = 100
# tib_bars = bars.imbalance_bar(test_data,ET_win,P_win,warm_len,mode = "TIB")

# vib_bars = bars.imbalance_bar(test_data,ET_win,P_win,warm_len,mode = "VIB")
# trb_bars = bars.tick_run_bar(test_data,ET_win,bt1_win,warm_len)
# vrb_bars = bars.vol_run_bar(test_data,ET_win,bt1_win,pos_vol_win,neg_vol_win,warm_up_len)

############################################################
#                Step 2: Generate Labels                   #
############################################################
# before generate labels, need to construct event dataframe to let the function know your need
events = pd.DataFrame()
events["start_idx"] = t_bars["start_idx"]
events["end_idx"] = t_bars["end_idx"]
events["target_rtn"] = 0.001
events["side"] = 0
price = test_data["Price"]

feature_mat =  fpre.meta_label(price, events, profit_take=1, stop_loss=1, inclu_vertical=False)
# initial feature matrix don't contain any features
# you can use add_features() function to add features into feature matrix 
price = test_data["Price"].values
# add highest value within each interval to feature matrix
feature_mat = fpre.add_features(feature_mat, price, feature_name="high", func=max) 
# add moving average of past 3 events at each sampling point to the feature matrix
# if func == None, the last value within sampling interval will be used
# if name is not defined, automatically assign name
MA3 = test_data["Price"].rolling(window=3).mean()
feature_mat = fpre.add_features(feature_mat, MA3.values) 

# before we proceed to cross validation, it should be note that
# if a feature is not stationary, it is not recommend to use cross validation
# use fractional differentiation to make it more stationary
f1 = fpre.frac_diff(feature_mat["high"], d=0.8, n_weight=20)
f2 = fpre.frac_diff(feature_mat["feature2"], d=0.9, thres=0.01)
feature_mat["stable_high"] = f1
feature_mat["stable_f2"] = f2

############################################################
#                Step 3: Cross Validation                  #
############################################################
# the output style is just like sk-learn cross validation
n_splits = 10
cv_indices = fm.purged_cross_validation(n_splits, feature_mat, embargo_pct=0.1, shuffle=True, random_seed=42)
# for each round of cross validation, if you want to do apply ensemble method
# sequential bootstrap method is also provided 
# e.g. for the first round of cross validation
first_train_idx = cv_indices[0][0]
first_test_idx = cv_indices[0][1]
train_data = feature_mat.iloc[first_train_idx,:]
label_start = train_data["feature_end"].values+1
label_end = train_data["label_point"].values
all_classifiers = fm.seq_bootstrap(label_start, label_end, n_classifier=3, n_sample=None, verbose=True)

bootstrap_data = []
for classifier in all_classifiers:
	data = train_data.iloc[classifier,:]
	bootstrap_data.append(data)

# and then you can start use bootstrap_data to train your own ensembled model!