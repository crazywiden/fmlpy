"""
implemented feature bars such as CUMSUM filter etc.
used to filter structured bars(imbalance bars/run bars etc.)
but whether to filter is optional 
"""
import pandas as pd 
import numpy as np 

def CUMSUM_filter(price, thres):
    """
    S_+(t) = max{0, S_+(t-1) + y(t) - y(t-1)}
    S_-(t) = min{0, S_-(t-1) + y(t) - y(t-1)}
    S(t) = max{S_+(t), -S_-(t)}
    sample when S(t) > thres

    @parameters:
    price -- 1d vector(list or np.ndarray)
    thres -- integer or vector
        thres is a vector means we allow different threshold at different stages
    @returns:
    CUMSUM_idx -- 1d vector
        each element is the starting index of each bar
    """
    CUMSUM_idx = []
    price_diff = np.diff(price)
    S_pos, S_neg = 0, 0 
    for i in range(1,len(price)):
        S_pos = max(0, S_pos + price_diff[i-1])
        S_neg = min(0, S_neg + price_diff[i-1])
        if max(S_pos, -S_neg) >= thres:
            CUMSUM_idx.append(i)
            S_pos, S_neg = 0, 0
            
    return np.array(CUMSUM_idx)

if __name__ == '__main__':
    test_data = pd.read_csv(r"D:\fmlpy\tests\bar_test_data.csv")
    price = test_data["Price"]
    a = CUMSUM_filter(price,thres=3000)
    print(a)


