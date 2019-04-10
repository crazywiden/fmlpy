"""
this script is used to calculate fractionally differentiated 
"""
import pandas as pd
import numpy as np


def frac_diff(price, d, thres=None, n_weight=None):
    '''
    This function is used to calculate fraction differenciation
    :param d: total number to iterate
    :param x: kind of some number
    :return: some calculated result
    '''
    if n_weight is not None:
        comb = _combine_weight(n_weight, d)
    else:
        comb = _combine_threshold(d, thres)
    length = len(comb) if len(comb)<len(price) else len(price)
    delta = len(price) - length + 1
    df = pd.DataFrame(columns=range(len(comb)))

    for i in range(length):
        df[i] = price[i:i+delta].values

    df = df.T
    result = df.apply(func=_one_frac, comb_list=comb, axis=0).to_list()
    res = price[:length-1].to_list()
    res.extend(result)
    return np.array(res)


def _combine_weight(n_weight,d):
    '''
    calculate combination number
    :param n:
    :return: a list of combination number
    '''
    result = [None] * (n_weight)
    sign = -1
    result[0] = 1
    for i in range(1, n_weight):
        result[i] = (d - i + 1) / i * result[i - 1] * sign
    return result


def _combine_threshold(d, threshold):
    '''
    calculate combination number
    :param d:
    :return: a list of combination number
    '''
    result = []
    sign = -1
    result.append(1)
    i = 1
    while True:
        number = (d - i + 1) / i * result[-1] * sign
        if abs(number) > threshold:
            result.append(number)
            i+=1
        else:
            break
    return result


def _one_frac(x, comb_list):
    answer = [a * b for a, b in zip(x[::-1], comb_list)]
    return np.sum(answer)


if __name__ == '__main__':
    price = [100, 200, 300, 400, 500]
    a = frac_diff(price, 0.5, thres=0.001)
    print(a)