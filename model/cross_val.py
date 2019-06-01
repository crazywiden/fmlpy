import time
import numpy as np 
import pandas as pd

class purgedCV:
    def __init__(self, n_splits, embargo_pct=0, shuffle=False, random_seed=42):
        """
        @parameters:
        n_splits -- int
            how many splits should we have
        embargo_pct -- double
            percentage of embargo with respect to whole length of time series
        shuffle -- binary
            default is False because time series data do not always stationary and shuffle may cause some issue
        random_state -- int
            seed for random generator if shuffle == True
        """
        self.n_splits = int(n_splits)
        self.shuffle = shuffle
        self.random_seed = random_seed
        self.embargo_pct = embargo_pct

    def split(self,X,y=None):
        """
        Generate indices to split data into training and test set.
        @parameters:
        X --  n_samples by n_features ndarray
            n_samples is number of bars 
            n_features is number of features
        y -- 1d ndarray
            length should be n_samples
        @yields:
        train_idx -- 1d ndarray
            The training set indices for that split.
        test_idx -- 1d ndarray
            The testing set indices for that split.
        """
        all_idx = pd.Series(np.arange(X.shape[0])) 
        mbrg = int(X.shape[0]*self.embargo_pct)
        test_starts=[(i[0],i[-1]+1) for i in np.array_split(all_idx.values,self.n_splits)]
        for i, j in test_starts:
            t0 = all_idx.index[i] # start of test set
            test_indices = all_idx.values[i:j]
            maxT1Idx = all_idx.index.searchsorted(all_idx[test_indices].max())
            train_indices = all_idx.index.searchsorted(all_idx[all_idx<=t0].index)
            if maxT1Idx < X.shape[0]: 
                train_indices=np.concatenate((train_indices,all_idx[maxT1Idx+mbrg:]))
            yield train_indices,test_indices


def purged_cross_validation(X,y, n_splits, embargo_pct=0, shuffle=False, random_seed=42):
    CV = purgedCV(n_splits, embargo_pct, shuffle, random_seed)
    return [(train, test) for train, test in CV.split(X,y)]

<<<<<<< HEAD
=======
if __name__ == '__main__':
    CV = purgedCV(n_splits=10)
    X = np.arange(100)
    y = np.arange(100)
    print(purged_cross_validation(X,y,n_splits=100))
>>>>>>> 5ed43473297ec1df2af86ede75af746e334331b0
