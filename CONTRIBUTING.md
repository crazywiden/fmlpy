# Development Guidelines
## Getting Started
+ Most of the functions in __fmlpy__ is based on the book [Advanced in Financial Machine Learning](https://drive.google.com/file/d/1XUr7phuMCQxBKyqFxeVcL2sOCRe5dq7Z/view?usp=sharing). If you are not familiar with the methods, please read the book first.
+ Financial data is usually of great size, so please pay a lot of attention to the speed of your code when you are implementing new method.

## Some basic rules
### Documentation
Detailed documentation is very helpful for both developers and users. So please write docstring for each function and class you write.

For docstring of functions, those information will be helpful  
+ purpose of this function
+ dependencies
+ input argument type and other info
+ return variable type and other info
```python
def tick_bar(data, time_win=10):
    """
    this function is used to calculate the tick bars of raw price data
    @required packages:
        pandas
    @parameters:
    data--dataframe
        at least have two columns: price and time
    time_win -- scalar
        time windows of aggregation of raw price data to calculate H,C,O,L
        default value is 10, represent 10 seconds
    @returns: 
    data--dataframe
        with columns of: time, high, low, close, open
    """
```
For docstring of class, those information will be helpful  
> not determined yet
### Naming Styles
For the sake of consistency, we recommend the following naming style  
+  *lower_case_underscore* for __variable__ name. Put subscript of a variable at back. Example: `close_price_t`, `feature_uniqueness`
+ *lower_case_underscore* for __function__ name. Example: `randome_forest()`,`meta_labelling`
+ *FirstLetterCapital* for __class__ name. Example: `Events`,`FeatureMat`

__Enjoy your coding and welcome for contribution!!__