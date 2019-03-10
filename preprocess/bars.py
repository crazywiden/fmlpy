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
import numpy as np
# from .. import fin_utils

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
        data = data.iloc[:, :2]
        data.columns = ["time","price"]
    else:
        data = data.iloc[:, :3]
        data.columns = ["time","price","vol"]
    return data

def _EMA(vec, win):
    """
    calculate the exponential moving average
    this version don't deal with NA value
    @parameters:
        vec-- vector
        win--scalar
    @returns:
        ema_series--vector
            the first win element is the same as vec
    """

    assert win>0 and win<len(vec), "the size of EMA window is not allowed"
    ema_series = vec.copy()
    N = len(ema_series)
    alpha = 2/(1+N)
    for i in range(win,N):
        ema_series[i] = (1-alpha)*ema_series[i-1] + alpha*vec[i]
    return ema_series

def _direction(price,vol=None,mode="tick"):
    """
    this function generate sequence b_t(in the book Chapter 2 section 3.2.1)
    formula: b_t = b_t - 1 is delta(p_t) == 0 else delta(p_t)/|delta(p_t)|
    @parameter:
        price--n by 1 array
        vol -- n by 1 array
            has same length with price,default is None
            needed if mode == "volume"
        mode -- string
            must be in ["tick","volume"]
    @returns:
        b_t -- n by 1 array
        each element is either 1 or -1 or 0
        represent the direction of price at t-1
    """
    assert mode in ["tick",'volume'],"please enter correct mode: tick/volume"
    if mode == "volume":
        if not vol:
            raise ValueError("volume data is required")
        data = np.array(price) * np.array(vol)
    else: # in this case mode == "tick"
        data = np.array(price)
    N = len(data)
    b_t = np.sign(np.diff(data)) # len(b_t) == N - 1
    b_t = np.insert(b_t,0,0) # now len(b_t) == N
    loc = np.where(b_t==0)[0][1:] # ignore the first element because it should be 0
    for i in loc:
        b_t[i] = b_t[i-1]
    return b_t

def _estimate_P(b_t, loc, window_size):
    """
    this function is used to calculate 2P(b_t=1)-1 as EMV of previous bt
    @parameters:
        b_t -- vector
            b_t is the direction series of original price
        loc -- scalar
            current bar location, i.e. where should we calcualte the EMA
        window_size -- scalar
            window_size of EMV
    @returs:
        P -- scalar
    """
    window_size = min(loc-1, window_size)
    ema_series = _EMA(b_t[:loc], window_size)
    return ema_series[loc-1]

def _estimate_ET(bar, window_size):
    """
    this function is used to calculate E[T] as EMV of previous bar length
    @requires:
        pandas 0.24.1
    @parameters:
        bar -- vector
            bar[i] is the length of i-the bar
        window_size -- scalar
            window_size of EMV
    @returns:
        E_T--scalar
    """
    N = len(bar)
    if N == 1:
        return bar
    elif N == 2:
        return np.mean(bar)
    elif N == 0:
        return 0
    window_size = min(N-1, window_size)
    # bar_ema = fin_utils.EMA(bar,window_size)
    bar_df = pd.DataFrame({'bar':bar})
    bar_ema = bar_df.ewm(span=window_size).mean()
    return bar_ema.values[-1]

def time_bar(data, time_window):
    '''
    Calculate HOLC for certain time window
    @requires:
        pandas
    @param:
        data: input data with time and price
        time_window: time window size, acceptable format and meaning are
            B         business day frequency
            C         custom business day frequency (experimental)
            D         calendar day frequency
            W         weekly frequency
            M         month end frequency
            SM        semi-month end frequency (15th and end of month)
            BM        business month end frequency
            CBM       custom business month end frequency
            MS        month start frequency
            SMS       semi-month start frequency (1st and 15th)
            BMS       business month start frequency
            CBMS      custom business month start frequency
            Q         quarter end frequency
            BQ        business quarter endfrequency
            QS        quarter start frequency
            BQS       business quarter start frequency
            A         year end frequency
            BA, BY    business year end frequency
            AS, YS    year start frequency
            BAS, BYS  business year start frequency
            BH        business hour frequency
            H         hourly frequency
            T, min    minutely frequency
            S         secondly frequency
            L, ms     milliseonds
            U         microseconds
            N, us     nanoseconds
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
    return result


def imbalance_bar(data,ET_window,P_window, warm_up_len = 100,mode="TIB"):
    """
    this function is used to calculate the tick imbalance bar
    @parameters:
        data--dataframe
            first column should be time second column should be price
        ET_window--scalar
            EMV window size to estimate E[T]
        P_window--scalar
            EMV window size to estimate 2P(b_t==1) - 1
        warm_up_len -- scalar
            how many data should we use to warm up
            default is 100
        mode -- string
            can only be "TIB"(tick imbalance bar) or "VIB"(volume imbalance bar)
    @returns:
        dataframe (start, stop, high, low, close, open)
    """
    assert mode in ["TIB","VIB"], "please enter mode of imbalance bar: TIB/VIB"
    if mode == "TIB":
        data = _preprocess(data)
    else:
        data = _preprocess(data, need_vol=True)

    N = data.shape[0]
    b_t = _direction(data["price"])
    if mode == "VIB":
        b_t = b_t * data["volume"]
    t0 = max(np.nonzero(b_t)[0][0], warm_up_len)
    bar = [t0]
    bar_len = 0
    E_T = _estimate_ET(bar, ET_window) # E_T warm up
    E_theta = E_T[0] * _EMA(b_t[:t0],win=min(t0-1,P_window))[0]
    while True:
        current_loc = sum(bar)
        theta_t = abs(np.cumsum(b_t[:-current_loc]))
        increment = np.where(theta_t > E_theta)[0]# np.where() will return a tuple
        if len(increment)==0: # if can't find any appropriate bar
            break  
        if bar[bar_len] + increment[0] >= N:
            break

        bar.append(bar[-1] + increment[0])
        bar_len += 1
        E_T = _estimate_ET(bar, ET_window)
        E_theta = E_T * _estimate_P(b_t, current_loc, P_window)

    return np.array(bar)



# test
if __name__ == '__main__':
    bar_test = pd.read_csv('../tests/bar_test_data.csv')
    bar_test = bar_test.iloc[:,1:]
    # print(bar_test.head())
    bar_loc = imbalance_bar(bar_test,ET_window=100,P_window=100, warm_up_len = 100,mode="TIB")
    # from timeit import Timer 
    # t = Timer(lambda: _direction(price))
    
