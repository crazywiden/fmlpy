import pandas as pd 
import numpy as np 

def _check_event_format(events):
    if not isinstance(events, pd.DataFrame):
        return False
    if not set(events.columns.values).issubset(["start_t","end_t","target_rtn","side"]):
        return False
    return True

def _get_label(price_seg, barrier, side, is_vertical):
    """
    get label, return, label point of each price segment
    @parameters:
    price_seg -- 1d vector
        price segment used to be labelled
    barrier -- 2 by 1 list
        barrier[0] is value of upper barrier, should be positive
        barrier[1] is value of lower barrier, should be negative
    side -- scalar 1 or -1 or 0
        side == 0 means take both upper barrier and lower barrier
        side == 1 means take only upper barrier
        side == -1 means take only lower barrier
    is_vertical -- binary
        is_vertical == True means label actual sign of return when hit vertical bar
        is_vertical == False means label 0 when hit vertical bar
    @returns:
    rtn -- double
        return of this bar
    label -- int
        sign of return, -1 or 1 or 0
    label_point -- int
        when the price hits the barrier
    """
    
    # get return of each point 
    rtn_vec = price_seg/price_seg[0] - 1 # note that rtn_vec[0] == 0
    upper_hit = np.argmax(rtn_vec>=barrier[0])
    lower_hit = np.argmax(rtn_vec<=barrier[1])
    if side == 0: # consider both upper barrier and lower barrier
        if upper_hit == 0 and lower_hit == 0: # doesn't hit upper barrier nor lower barrier
            if is_vertical:
                rtn = rtn_vec[-1]
                label = np.sign(rtn)
                label_point = len(price_seg)
            else:
                rtn,label = 0, 0
                label_point = len(price_seg)
        elif (upper_hit < lower_hit and upper_hit!=0) or lower_hit == 0: # hit upper barrier before lower barrier
            rtn = rtn_vec[upper_hit]
            label = np.sign(rtn)
            label_point = upper_hit
        elif (lower_hit < upper_hit and lower_hit!=0) or upper_hit == 0: # hit lower barrier before upper barrier
            rtn = rtn_vec[lower_hit]
            label = np.sign(rtn)
            label_point = lower_hit
        
    elif side == 1: # only consider upper barrier
        if upper_hit == 0: # doesn't hit upper barrier
            if is_vertical:
                rtn = rtn_vec[-1]
                label = np.sign(rtn)
                label_point = len(price_seg)
            else:
                rtn,label = 0, 0
                label_point = len(price_seg)
        else: # hit upper barrier
            rtn = rtn_vec[upper_hit]
            label = np.sign(rtn)
            label_point = upper_hit

    elif side == -1: # only consider lower barrier
        if lower_hit == 0: # doesn't hit lower barrier
            if is_vertical:
                rtn = rtn_vec[-1]
                label = np.sign(rtn)
                label_point = len(price_seg)
            else:
                rtn = rtn_vec[lower_hit]
                label = np.sign(rtn)
                label_point = lower_hit 

    return rtn, label, label_point




def meta_label(price, events, profit_take, stop_loss, is_vertical=True):
    """
    use tripple barrier method to label data 
    @parameters:
    prices-- 1d vector
    events--dataframe
        start_t: start time of each bar
        end_t: end time of each bar
        target_rtn: threshold return of upper and lower bar
        side: side[i] == 0 means take both upper barrier and lower barrier
              side[i] == 1 means take only upper barrier
              side[i] == -1 means take only lower barrier
    profit_take: double
        multiplier of target_rtn
    stop_loss: double
        multiplier of target_rtn
    is_vertical: binary, default is True
        is_vertical == True means label actual sign of return when hit vertical bar
        is_vertical == False means label 0 when hit vertical bar
    @returns:
    labelled -- dataframe
        feature_start: start point of feature bar
        feature_end: end point of feature bar
        label_point: time when prices hit the barrier
        label: 1(hit upper barrier) or -1(hit lower barrier) or 0(hit vertical barrier and is_vertical==False)
        return: actual return
    """
    if not _check_event_format(events): # check the name of columns
        raise ValueError("events should be a dataframe with columns: start_t/end_t/target_rtn/side")

    N_bar = events.shape[0]
    feature_start = events["start_t"].values
    feature_end = events["end_t"].values
    target_rtn = events["target_rtn"].values
    side = events["side"].values
    label_point = np.zeros(N_bar)
    label = np.zeros(N_bar)
    rtn = np.zeros(N_bar)

    for i in range(N_bar):
        barrier = [profit_take*target_rtn[i], -stop_loss*target_rtn[i]]
        rtn[i], label[i], tmp_point = _get_label(price[feature_start[i]:feature_end[i]],\
                                                 barrier, side[i], is_vertical)
        label_point[i] = i + tmp_point

    labelled = pd.DataFrame({"feature_start":feature_start, "feature_end":feature_end,\
        "label_point":label_point, "label":label,"return":rtn})

    return labelled

def add_features(feature_mat, features, feature_name=None):
    """
    add feature series generated by price/vwap/vol etc. to feature matrix
    @parameters:
    feature_mat -- dataframe
        basically output of meta_label() function
        feature_start: start point of feature bar
        feature_end: end point of feature bar
        label_point: time when prices hit the barrier
        label: 1(hit upper barrier) or -1(hit lower barrier) or 0(hit vertical barrier and is_vertical==False)
        return: actual return
    features -- np.ndarray
        could be 1d vector, which means only add one feature to the feature matrix
        also could be n by 1 matrix, with each column as a feature
        length of each feature should be same as raw price series
    feature_name -- list of strings
        each element corresponding to the name of one feature
        len(feature_name) == features.shape[1]
        default is None, just give "feature1","feature2",... to each feature
    @returns:
    feature_mat -- dataframe
        just the feature_mat in input added more columns 
    """
    pass