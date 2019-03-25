"""
this script is used to calculate fractionally differentiated 
and provide option to test the stationary of a series
"""
def frac_diff(n, k, x):
    '''
    This function is used to calculate fraction differenciation
    :param n: total number to iterate
    :param k: don't know how to say in English
    :param x: kind of some number
    :return: some calculated result
    '''
    comb_list = _combine(n, k)
    answer = [a*b for a,b in zip(x,comb_list)]
    return answer


def _combine(n, k):
    '''
    calculate combination number
    :param n:
    :param k:
    :return: a list of combination number
    '''
    result = [None]*n
    sign = 1 if n % 2 == 0 else -1
    result[0] = 1*sign
    for i in range(1, n+1):
        sign = -sign
        result[i] = (n-i+1)/i*result[i-1]*sign
    return result
