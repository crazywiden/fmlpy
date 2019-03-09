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
        data = data.iloc[:, [1,3]]
        data.columns = ["time","price"]
    else:
        data = data.iloc[:, [1,3,2]]
        data.columns = ["time","vol","price"]
    return data



def time_bar(data, time_window):
    '''
    Calculate HOLC for certain time window
    @requires:
        pandas
    @param:
        data: input data with time and price
        time_window: time window size
    @return:
        dataframe (start, stop, high, low, close, open)
    '''
    data = _preprocess(data)
    data = data.assign(time= pd.to_datetime(data['time']))
    data = data.resample(time_window, on='time')
    aggregated_data = data.agg(['min', 'max', 'first', 'last'])
    times = aggregated_data['time']
    times.columns = ['min', 'max', 'start', 'stop']
    times = times[['start', 'stop']]
    price = aggregated_data['price']
    price.columns = ['low', 'high', 'open', 'close']
    result = pd.concat([times, price], axis=1, sort=False)
    result = result.reset_index()
    result = result.drop(['time'], axis=1)
    result = result.dropna()
    return result


def volume_bar(data, size):
    '''
    Calculate HOLC for a certain volume
    @requires:
        pandas
    @parameters:
        data: input data with time, price and volume
        size: input volume bar, integer
    @return:
        dataframe (start, stop, high, low, close, open)
    '''
    data = _preprocess(data, True)
    if not isinstance(size, int):
        raise TypeError("Size should be an integer")
    data.loc[:, 'vol'] = pd.to_numeric(data['vol'])
    data.loc[:, 'cumsum'] = data['vol'].cumsum()
    data['cumsum'] = data['cumsum'] // size
    aggregated_data = data.groupby('cumsum').agg({'time': ['first', 'last'], 'price': ['min', 'max', 'first', 'last']})
    aggregated_data.columns = [' '.join(col).strip() for col in aggregated_data.columns.values]
    aggregated_data.columns = ['start', 'stop', 'low', 'high', 'open', 'close']
    result = aggregated_data.reset_index()
    result = result.drop(['cumsum'], axis=1)
    result = result.dropna()
    return result


def dollar_bar(data, bar):
    '''
    Calculate HOLC for a certain dollar
    @requires:
        pandas
    @parameters:
        data: input data with time, price and volume
        size: input dollar bar, integer
    @return:
        dataframe (start, stop, high, low, close, open)
    '''
    data = _preprocess(data, True)
    if not isinstance(bar, int):
        raise TypeError("Dollar bar should be an integer")
    data.loc[:, 'vol'] = pd.to_numeric(data['vol'])
    data['dollar'] = data['price'] * data['vol']
    data.loc[:, 'cumsum'] = data['dollar'].cumsum()
    data['cumsum'] = data['cumsum'] // bar
    aggregated_data = data.groupby('cumsum').agg({'time': ['first', 'last'], 'price': ['min', 'max', 'first', 'last']})
    aggregated_data.columns = [' '.join(col).strip() for col in aggregated_data.columns.values]
    aggregated_data.columns = ['start', 'stop', 'low', 'high', 'open', 'close']
    result = aggregated_data.reset_index()
    result = result.drop(['cumsum'], axis=1)
    result = result.dropna()
    result.to_csv('result.csv')
    return result

# test
bar_test = pd.read_csv('../tests/bar_test_data.csv')
# print(time_bar(bar_test, '3s'))
# print(volume_bar(bar_test, 200))
dollar_bar(bar_test, 200000000)