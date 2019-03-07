"""
this script main implement 7 functions and their supporting functions
time_bar()
volume_bar()
dollar_bar()
tick_imbalance_bar()
volume_imbalance_bar()
tick_run_bar()
volume_run_bar()
"""
def _preprocess(data,T=None,price=None,vol=None):
  """
  this function is used to do the following things:
  1. aggregate the data input as a dataframe
  2. exception handling
  """
