"""
this script is used to calculate fractionally differentiated 
and provide option to test the stationary of a series
"""
import pandas as pd
import numpy as np

def frac_diff(n, x):
    '''
    This function is used to calculate fraction differenciation
    :param n: total number to iterate
    :param x: kind of some number
    :return: some calculated result
    '''
    length = len(x) - n
    df = pd.DataFrame(columns=range(length))
    for i in range(n+1):
        df.loc[len(df), :] = x[i: i+length]
    result = df.apply(func=_one_frac, base=n, axis=0).to_list()
    res = x[:n] + result
    return res


def _combine(n):
    '''
    calculate combination number
    :param n:
    :return: a list of combination number
    '''
    result = [None] * (n+1)
    sign = -1
    result[0] = 1
    for i in range(1, n+1):
        result[i] = (n-i+1)/i*result[i-1]*sign
    return result


def _one_frac(x, base):
    comb_list = _combine(base)
    answer = [a * b for a, b in zip(x[::-1], comb_list)]
    return np.sum(answer)


res = frac_diff(2, [1,2,3,4,5,6,7,8,9,10])
print(res)