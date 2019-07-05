# fmlpy
Welcome to Financial Machine Learning in Python! 

This package is used to apply machine learning methods to financial data, which generally has very low SNR(signal to noise ratio) and thus hard to apply ML directly. You can find more detailed explaination of methods implemented in this package in [Advances in Financial Machine Learning](https://drive.google.com/file/d/1XUr7phuMCQxBKyqFxeVcL2sOCRe5dq7Z/view?usp=sharing). Also you can find R version of this package at [fmlr](https://github.com/larryleihua/fmlr). 

## What is this package doing?
There are mainly three obstacles people may encouter when they are trying to apply machine learning on financial data:
1. Financial data are usually very heavy. The memory needed to store the limit order book of a single stock is usually at TB scale, so it's extremly slow if the algorithm needs to train a lot of parameters; 
2. Signal to Noise ratio in financial data is very low. Since the market has too many noises, it's hard to detect or even define what signla is, which may easily lead to overfitting;
3. Financial data are highly correlated, which violates the independent assumption of most machine learning model. Since financial data are mostly time series data, it's hard to do cross validation with it because if we use "*future data*" to predict "*past data*", the accuracy can't really show the real performance of the model.

To deal with the three problems above, we use the following scheme before we apply any traditional machine learning algorithm to financial data:
1. **Sample data into information bars.** The goal of this step is to reduce the size of data and only preserve the data with information.
2. **Use meta-label method to label the bars.**  The goal of this step is to build a feature matrix so that traditional machine learning algorithm can be applied.
3. **Split data using purged cross validation.** The goal of this step is to avoid information leakage when cross validate the model by training on "*future data*" and testing on "*past data*".

## Framework
This package included four modules listed below  

+ __preprocessing__  
    Used to preprocess raw price series. Including generate all kinds of structured bars, meta-labelling, generate fractionally differentiated series etc.
+ __model__  
    Used to train machine learning models. Mainly deal with cross-validation and sequential boostrap method. 
+ __backtest__  
    Used to back test quantatitive investment strategies.   
    __* This module will not be included in the first version__
+ __tests__  
    Used to test the correctness of the code during development and provide examples to users after the package is deployed. 

## Dependecy
+ pandas 0.24.1
+ numpy 1.16.1


## Installation
This package is under developement. Will be provided once we are ready.

## Examples
See [this pipeline](https://github.com/crazywiden/fmlpy/blob/master/tests/pipeline_example.py) for how to use most of the functions in this packagge.

## Contribute
Salute to My King!!

![](https://drive.google.com/uc?export=view&id=1XjO7_k6Qo0BwICw8TsAo72vFDqrKKTZh)  
Also thanks to anyone who can help!! Please read our [Contributing Guidelines](https://github.com/crazywiden/pyfml/blob/master/CONTRIBUTING.md) before contributing.
