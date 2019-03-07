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
def _preprocess(data, need_vol=False):
  """
  this function is used to do the following things:
  1. exception handling (determine if the data is ideal data)
  2. aggregate the data input as a dataframe
  Note that this function is a private function only for this module
  @requires:
    pandas
  @parameters:
  data--dataframe
    default is None
    the ideal data should have at least one columns: price
    if only one column, then we need add another column T (use index of each row)
    if two column, treat the first column as T
    if need_vol is True, then must have three columns and treat the third column as Volume
  need_vol--binary
    default is False
    when need_vol == False, the data variable can have two columns
    when need_vol == True, the data variable should have at least three columns with the last column is volume
  @returns:
    data-- dataframe
    with two or three columns
    if two column, treat the first column as T
    if need_vol is True, then must have three columns and treat the third column as Volume
  """
  if not isinstance(data,pd.DataFrame):
    raise TypeError("the input should be DataFrame")
  return data



def time_bar(data, time_window):
    data = preproc(data)

    # return: dataframe (start, stop, HLOC)
    # time win intergeer
    # exception?

def volume_bar(data, size):
    # return dataframe