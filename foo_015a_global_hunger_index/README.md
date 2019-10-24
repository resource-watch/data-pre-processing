## Global Hunger Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the 2019 Global Hunger Index](https://www.globalhungerindex.org/pdf/en/2019.pdf) for [display on Resource Watch](https://resourcewatch.org/data/explore/foo_015a_global_hunger_index).

This analysis is done in Python.

Below we describe the steps to preprocess a csv file extracted from the pdf report
1. Import packages and define directory
```
import os
import pandas as pd
```
# find current directory

path= os.getcwd()

# define directory

path = '/Users/tinahuang/Desktop' # you can replace this string with your  own path
os.chdir(path)
print(path) # check your path
```
2. Download data from the 2019 Global Hunger Index report :https://www.globalhungerindex.org/pdf/en/2019.pdf
   Copy and paste data from the pdf report into a csv, replace "-" with NaN, we call this csv: foo_015a_global_hunger_index - Sheet1.csv
3. Process the dataset in python
```
# read in csv file as Dataframe
global_hunger_index_2019_df = pd.read_csv('foo_015a_global_hunger_index - Sheet1.csv')
# clean the dataframe, replace <5 with 5, replace NaN's with null
global_hunger_index_2019_df= global_hunger_index_2019_df.replace('<5', 5)
global_hunger_index_2019_df=global_hunger_index_2019_df.where((pd.notnull(global_hunger_index_2019_df)), None)
global_hunger_index_2019_df

# we will only use column 1:5, subset the data frame
global_hunger_index_2019_df= global_hunger_index_2019_df[['Country', '2000', '2005', '2010', '2019'] ]
# examine new dataframe
global_hunger_index_2019_df.head()
#convert tables from wide form (each year is a column) to long form (a single column of years and a single column of values)
hunger_index_long = pd.melt (global_hunger_index_2019_df, id_vars= ['Country'] , var_name = 'year', value_name = '2000')
# examine the new data frame
hunger_index_long
# change the name of index score column
hunger_index_long.rename (columns = {'2000':'hunger_index_score'}, inplace= True)
hunger_index_long
# examine each column's data type
hunger_index_long.dtypes
#convert year and hunger_index_score columns from object to number
hunger_index_long.year=hunger_index_long.year.astype('int64')
hunger_index_long.hunger_index_score = hunger_index_long.hunger_index_score.astype('float64')
hunger_index_long=hunger_index_long.where((pd.notnull(hunger_index_long)), None)
hunger_index_long

```
