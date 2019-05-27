import pandas as pd 
import numpy as np 

def _check_event_format(events):
    if not isinstance(events, pd.DataFrame):
        return False
    if not set(events.columns.values).issubset(["start_t","end_t","target_rtn","side"]):
        return False
    return True

def _get_label(price_seg, barrier, side, inclu_vertical):
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
    inclu_vertical -- binary
        inclu_vertical == True means include the labels when hit verticle barrier
        inclu_vertical == False means exclude the labels when hit verticle barrier
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

    # initially, assign -2 to label to indicate price hit vertical barrier
    # if inclu_vertical == True, we turn label==-2 to label==0
    # in other case, bar with label == -2 will be excluded
    if side == 0: # consider both upper barrier and lower barrier
        if upper_hit == 0 and lower_hit == 0: # doesn't hit upper barrier nor lower barrier
            rtn = rtn_vec[-1]
            label = -2 
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
        if upper_hit == 0 and lower_hit == 0: # hit vertical barrier
            rtn = rtn_vec[-1]
            label = -2
            label_point = len(price_seg)
        elif upper_hit == 0: # hit lower barrier but not hit vertical barrier
            rtn = rtn_vec[-1]
            label = 0
            label_point = len(price_seg)
        else: # hit upper barrier
            rtn = rtn_vec[upper_hit]
            label = np.sign(rtn)
            label_point = upper_hit

    elif side == -1: # only consider lower barrier
        if lower_hit == 0 and upper_hit==0: # hit vertical barrier
            rtn = rtn_vec[-1]
            label = -2
            label_point = len(price_seg)
        elif lower_hit == 0: # hit upper barrier but not hit vertical barrier
            rtn = rtn_vec[-1]
            label = 0
            label_point = len(price_seg)
        else:
            rtn = rtn_vec[lower_hit]
            label = np.sign(rtn)
            label_point = lower_hit 

    if inclu_vertical and label == -2:
        label = 0

    return rtn, label, label_point




def meta_label(price, events, profit_take, stop_loss, inclu_vertical=False):
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
    inclu_vertical: binary, default is False
        inclu_vertical == True means include the labels when hit verticle barrier
        inclu_vertical == False means exclude the labels when hit verticle barrier
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
    label_start = events["start_t"].values
    label_end = np.minimum(events["end_t"].values, len(price)-1)
    target_rtn = events["target_rtn"].values
    side = events["side"].values
    label_point = np.zeros(N_bar,dtype=int)
    label = np.zeros(N_bar,dtype=int)
    rtn = np.zeros(N_bar)
    for i in range(N_bar):
        barrier = [profit_take*target_rtn[i], -stop_loss*target_rtn[i]]
        rtn[i], label[i], tmp_point = _get_label(price[label_start[i]:(label_end[i]+1)],\
                                                 barrier, side[i], inclu_vertical)
        label_point[i] = label_start[i] + tmp_point

    # previous time point of label_start is end of previous feature bar
    feature_start = np.insert(label_start[:-1]-1,0, 0)
    feature_end = label_start-1

    labelled = pd.DataFrame({"feature_start":feature_start, "feature_end":feature_end,\
        "label_point":label_point, "label":label,"return":rtn})
    # if we don't need bars that hitted vertical barrier
    # we will remove bars with label==-2
    # else we turn bars with label==-2 to 0
    if not inclu_vertical: 
        labelled = labelled.drop(labelled[labelled["label"]==-2].index)
        labelled = labelled.reset_index()
    else:
        labelled[labelled["label"]==-2] = 0
    return labelled

def add_features(feature_mat, features, feature_name=None, func=None):
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
    if not func:
        new_feature = features[feature_mat["feature_end"]]

    else:
        new_feature = [func(features,start,end) for start, end in zip(feature_mat["feature_start"], feature_mat["feature_end"])]

    if not feature_name:
        feature_name = "feature_" + (feature_mat.shape[1]-5)

    feature_mat[feature_name] = new_feature

    # fill NA with previous value
    feature_mat.fillna(method="ffill")
    return feature_mat
