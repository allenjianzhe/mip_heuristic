
# coding: utf-8

# In[1]:

import pandas as pd


# In[8]:

def generate_cutomer_data(size_of_customer):
    from random import randint as uniform_dist
    data = pd.DataFrame(columns=['Customer_Id', 'Final_Destination', 'Demand','Due_Date','Penalty'])
    for i in range(size_of_customer):
        data.loc[i] = [i, 'SS', uniform_dist(50,250), uniform_dist(6,35), 50]
    return data


# In[9]:

d = generate_cutomer_data(10)


# In[11]:

d.to_csv('c:/Users/MacBook Air/Desktop/customer.csv', index=False)


# In[12]:

d = pd.read_csv('c:/Users/MacBook Air/Desktop/customer.csv')


# In[39]:

customer=[]
for i,row in d.iterrows():
    customer.append(row.tolist())
print customer

# In[36]:

type(row[1][''])


# In[40]:

customer


# In[41]:

get_ipython().magic(u'pinfo pd.DataFrame')


# In[ ]:



