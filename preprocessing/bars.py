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
import pandas as pd
from functools import reduce

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
    if not need_vol:
        data = data.iloc[:,:2]
        data.columns = ["time","price"]
    else:
        data = data.iloc[:,:3]
        data.columns = ["time","price","vol"]
    return data



def time_bar(data, time_window):
    '''
    Calculate HOLC for certain time window
    @requires:
        pandas, functools
    @param:
        data: input data with time and price
        time_window: time window size
    @return:
        dataframe (start, stop, high, low, close, open)
    '''
    data = _preprocess(data)
    time_window = pd.Timedelta(time_window)
    merged = data.groupby('time').agg(['min', 'max', 'first', 'last']).reset_index() #there might be something wrong here
    start = end = pd.to_datetime(data['time'][0])
    lo = float("inf")
    hi = 0
    open = merged.iloc[0]['price']['first']
    result = pd.DataFrame(columns=['start', 'stop', 'high', 'low', 'close', 'open'])
    for index, row in merged.iterrows():
        if lo < row.price['min']:
            lo = row.price['min']
        if hi > row.price['max']:
            hi = row.price['max']
        cur = pd.to_datetime(row['time'])
        if cur < start + time_window:
            end = cur
        else:
            result.append(pd.DataFrame([start, end, hi, lo, row.price['last'], open]))
            start = end
            open = row.price['first']
            if cur < start + time_window:
                end = cur
            else:
                result.append(pd.DataFrame([start, end, hi, lo, row.price['last'], open]))
                start = cur
    return result


def volume_bar(data, size):
    '''
    Calculate HOLC for a certain volume
    :param data: input data with time and price
    :param size: input volume bar
    :return: dataframe (start, stop, high, low, close, open)
    '''
    data = _preprocess(data, True)
