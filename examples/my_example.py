"""
my_example.py
==========================

Here is a plot example
"""

import matplotlib.pyplot as plt

_ = plt.plot([1,2,3])

#%%
# pandas dataframes have a html representation, and this is captured:

import pandas as pd

df = pd.DataFrame({'col1': [1,2,3],
                   'col2': [4,5,6]})
print( df )

s = pd.Series([1,2,3])
