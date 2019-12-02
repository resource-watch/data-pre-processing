#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os 
import pandas as pd 


# In[3]:


# find current directory
path= os.getcwd()


# In[4]:


print(path)


# In[5]:


# define directory
path = '/Users/tinahuang/Desktop' # define your own path
os.chdir(path)


# In[8]:


print(path) # check your path


# In[9]:


# Download data from the 2019 Global Hunger Index report :https://www.globalhungerindex.org/pdf/en/2019.pdf
# copy and paste data from the pdf report into a csv, replace "-" with NaN


# In[10]:


# read in csv file as Dataframe 
global_hunger_index_2019_df = pd.read_csv('foo_015a_global_hunger_index - Sheet1.csv')


# In[11]:


# examine this data frame 
global_hunger_index_2019_df.head()


# In[12]:


# clean the dataframe, replace <5 with 5, replace NaN's with null
global_hunger_index_2019_df= global_hunger_index_2019_df.replace('<5', 5)
global_hunger_index_2019_df=global_hunger_index_2019_df.where((pd.notnull(global_hunger_index_2019_df)), None)
global_hunger_index_2019_df


# In[13]:


# we will only use column 1:5, subset the data frame
global_hunger_index_2019_df= global_hunger_index_2019_df[['Country', '2000', '2005', '2010', '2019'] ]


# In[14]:


# examine new dataframe 
global_hunger_index_2019_df.head()


# In[1]:


#convert table from wide form (each year is a column) to long form (a single column of years and a single column of values)
hunger_index_long = pd.melt (global_hunger_index_2019_df, id_vars= ['Country'] , var_name = 'year', value_name = 'hunger_index_score')


# In[16]:


# examine the new data frame 
hunger_index_long


# In[18]:


# examine each column's data type
hunger_index_long.dtypes


# In[19]:


#convert year and hunger_index_score columns from object to number
hunger_index_long.year=hunger_index_long.year.astype('int64')
hunger_index_long.hunger_index_score = hunger_index_long.hunger_index_score.astype('float64')
hunger_index_long=hunger_index_long.where((pd.notnull(hunger_index_long)), None)
hunger_index_long





