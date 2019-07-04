import pandas as pd
import numpy as np
import itertools

def _bar2df(bars,data):
    """
    get subset of data according to the location provided by bar_loc
    @parameters:
    data -- dataframe
        first column should be time second column should be price
    bars -- np.array
        each element in bars represent the length of that bar
    @returns:
    res -- dataframe
        dataframe (start, stop, high, low, close, open)
    """
    tmp = list(map(lambda x: [x[0] for _ in range(x[1])],list(enumerate(bars))))
    labels = list(itertools.chain(*tmp))
    data["labels"] = labels
    aggregation_condition = {'time': ['first', 'last'], \
                             'price': ['min', 'max', 'first', 'last']}
    res = data.groupby("labels",as_index=False).agg(aggregation_condition)
    res.columns = ['_'.join(col) for col in res.columns.values]
    res = res.drop(["labels_"],axis=1)
    res.columns = ['start', 'stop', 'low', 'high', 'open', 'close']
    return res


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

    # assert win>0 and win<len(vec), "the size of EMA window is not allowed"
    alpha = 2/(1+win)
    if win == 1 or len(vec) == 1:
        k = 1
    else: # why we need this?? --  to save memory using approximately 
        err = 0.000001
        k = np.ceil(np.log(err) / np.log(1-alpha))

    N = int(min(len(vec), k))
    ema_series = [0 for _ in range(N)]
    ema_series[0] = vec[0]
    for i in range(1,N):
        ema_series[i] = alpha*vec[i] + (1-alpha)*ema_series[i-1]
    return ema_series

def _direction(price,vol=None,mode="tick"):
    """
    this function generate sequence b_t(in the book Chapter 2 section 3.2.1)
    formula: b_t = b_{t-1} if delta(p_t) == 0 else delta(p_t)/|delta(p_t)|
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
        bar: input dollar bar, integer
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
    calculate the tick imbalance bar
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
        b_t = np.array(b_t * data["vol"])
    E_T = warm_up_len
    E_theta = E_T * 0.5 # without prior knowledge it's reasonable to assume P(b_t==1) = 0.5

    # length of first bar
    t0 = np.where(abs(np.cumsum(b_t))>=E_theta)[0]
    if len(t0) == 0:
        raise ValueError("No such bar can be created!")

    bar = [t0[0]+1]
    bar_len = 0
    current_loc = sum(bar)
    while True:
        E_T = _EMA(bar, ET_window)[-1]
        P_estimate = _EMA(b_t[:current_loc], P_window)[-1]
        E_theta = E_T * abs(P_estimate)

        theta_t = abs(np.cumsum(b_t[current_loc:]))
        increment = np.where(theta_t >= E_theta)[0] # np.where() will return a tuple
        
        if len(increment)==0: # if can't find any appropriate bar
            bar.append(data.shape[0] - current_loc)
            break  
        if bar[bar_len] + (increment[0]+1) >= N:
            bar.append(data.shape[0] - current_loc)
            break
        bar.append(increment[0]+1)# python start from 0 but we want to store the length of each bar
        current_loc += (increment[0]+1)
        bar_len += 1
    result = _bar2df(bar,data)
    return result

def tick_run_bar(data, ET_window, bt1_window, warm_up_len=100):
    """
    calculate the tick run bar
    note that this function has different output with fmlr::bar_tick_imbalance()
    reason is these two function adopted different method to calculate EMA
    don't know which method is correct yet
    @parameters:
        data--dataframe
            first column should be time second column should be price
        ET_window--scalar
            EMV window size to estimate E[T]
        bt1_window--scalar
            EMV window size to estimate proportion of b_t==1 in each bar
        warm_up_len -- scalar
            how many data should we use to warm up
            default is 100
    @returns:
        dataframe (start, stop, high, low, close, open)
    """
    data = _preprocess(data)
    b_t = _direction(data["price"])
    N = data.shape[0]

    # initialize E_T, P(b_t=1)
    bar = []
    bar_len = 0
    P_bt1_vec = []
    E_T = warm_up_len
    E_theta = E_T * 0.5
    
    pos_cnt = 0
    neg_cnt = 0
    increment = 0
    # start updating
    for i in range(N):
        if b_t[i] == 1:
            pos_cnt += 1
        elif b_t[i] == -1:
            neg_cnt += 1
        increment += 1

        if max(pos_cnt,neg_cnt) >= E_theta: # max(pos_cnt,neg_cnt) is theta_t
            # print(increment)
            bar.append(increment) # in this scenario we sample a bar
            bar_len += 1

            P_bt1_vec.append(pos_cnt/increment)
            pos_cnt, neg_cnt = 0, 0 # reset \sum_{bt==1} to 0
            increment = 0
            # recalculate E_theta
            E_T = _EMA(bar, ET_window)[-1]
            P_bt1 = _EMA(P_bt1_vec, bt1_window)[-1]
            E_theta = E_T * max(P_bt1, 1 - P_bt1)
    bar.append(data.shape[0] - sum(bar))
    result = _bar2df(bar,data)
    return result

def vol_run_bar(data,ET_window,bt1_window,pos_vol_window,neg_vol_window,warm_up_len=100):
    """
    calculate the tick run bar
    use E_theta = E_T * max(E[v|b_t=1]*P_bt1, E[v|b_t=-1]*(1-P_bt1))
    as warm up method
    @parameters:
        data--dataframe
            first column should be time second column should be price
        ET_window--scalar
            EMV window size to estimate E[T]
        bt1_window--scalar
            EMV window size to estimate proportion of b_t==1 in each bar
        pos_vol_window--scalar
            EMV window size to estimate E(v_t|b_t==1) 
        neg_vol_window--scalar
            EMV window size to estimate E(v_t|b_t==-1)
        warm_up_len -- scalar
            how many data should we use to warm up
            default is 100
    @returns:
        dataframe (start, stop, high, low, close, open)
    """
    data = _preprocess(data, need_vol=True)
    b_t = _direction(data["price"])
    vol = data["vol"]
    N = data.shape[0]

    # initialize E_T, P(b_t=1), E[v_t|b_t==1], E[v_t|b_t==-1]
    t0 = warm_up_len
    E_T = t0

    P_bt1 = np.count_nonzero(b_t[:t0]==1)/t0
    P_bt1_vec = [P_bt1]

    pos_loc = np.where(b_t[:t0]==1)[0]
    if len(pos_loc) == 0:
        pos_vol_vec = [0]
    else:
        pos_vol_vec = [np.mean(vol[pos_loc].values)]

    neg_loc = np.where(b_t[:t0]==1)[0]
    if len(neg_loc) == 0:
        neg_vol_vec = [0]
    else:
        neg_vol_vec = [np.mean(vol[neg_loc].values)]
    E_theta = E_T * max(pos_vol_vec[-1]*P_bt1, neg_vol_vec[-1]*(1-P_bt1))
    
    bar = []
    bar_len = 0
    pos_vol,neg_vol = 0, 0
    pos_cnt,neg_cnt = 0, 0
    increment = 0
    # start updating
    for i in range(N):
        if b_t[i] == 1:
            pos_vol += vol[i]
            pos_cnt += 1
        elif b_t[i] == -1:
            neg_vol += vol[i]
            neg_cnt += 1
        increment += 1

        if max(pos_vol,neg_vol) >= E_theta: # max(pos_cnt,neg_cnt) is theta_t
            bar.append(increment) # in this scenario we sample a bar
            bar_len += 1

            P_bt1_vec.append(pos_cnt/increment)
            pos_vol_vec.append(pos_vol/increment)
            neg_vol_vec.append(neg_vol/increment)

            pos_cnt, neg_cnt = 0, 0 # reset \sum_{b_t==1} b_t to 0
            pos_vol, neg_vol = 0, 0 # reset \sum_{b_t==1} v_t to 0
            increment = 0
            # recalculate E_theta
            E_T = _EMA(bar, ET_window)[-1]
            P_bt1 = _EMA(P_bt1_vec, bt1_window)[-1]
            E_v_bt_pos = _EMA(pos_vol_vec,pos_vol_window)[-1]
            E_v_bt_neg = _EMA(neg_vol_vec,neg_vol_window)[-1]
            E_theta = E_T * max(E_v_bt_pos*P_bt1, E_v_bt_neg * (1 - P_bt1))
    bar.append(data.shape[0] - sum(bar))
    result = _bar2df(bar,data)
    return result

