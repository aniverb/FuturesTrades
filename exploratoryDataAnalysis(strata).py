#Jupyter Notebook Code: NOT MEANT TO BE EXECUTABLE

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
get_ipython().magic(u'matplotlib inline')
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from scipy import stats

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

dataset=pd.read_csv('trades_count_regression_2016-11-18.txt', sep='\t')
dataset.head()

#making raw (not Box-Cox transformed) trade volume histogram for entire population
plt.figure(figsize=(6, 5))
plt.hist(dataset.DayTradeTotal); plt.title("Original Trade Volume");
plt.savefig('hist_orig.png', bbox_inches='tight') 

#making trade volume histogram for entire population
plt.figure(figsize=(6, 5))
plt.hist(dataset.TradeTotBCTrans); plt.title("BoxCox Transformed Trade Volume");
plt.savefig('hist_bc.png', bbox_inches='tight') 

#making trade volume histograms by market
plt.figure(figsize=(15, 15))
for i, j in enumerate(np.unique(dataset.ProductType)):
    subset=dataset.loc[dataset.ProductType==j]
    plt.subplot(3,2,i+1);
    plt.subplots_adjust(hspace=.3);
    plt.subplots_adjust(wspace=.5);
    plt.hist(subset['TradeTotBCTrans']); plt.title(j+" BoxCox Transformed Trade Volume");

plt.savefig('types_bc_hist.png', bbox_inches='tight')    

#making trade volume vs time to maturity plot for entire population
plt.figure(figsize=(6, 5))
plt.plot(dataset[['TimeToMaturity']], dataset[['TradeTotBCTrans']], '.'); plt.xlabel('TimeToMaturity'); 
plt.ylabel('TradeTotBCTrans');
plt.savefig('time_to_mat.png', bbox_inches='tight') 

#making trade volume vs day plot for entire population
plt.figure(figsize=(6, 5))
plt.plot(dataset[['Day']], dataset[['TradeTotBCTrans']], '.'); plt.xlabel('Day'); plt.ylabel('TradeTotBCTrans');
plt.ylabel('TradeTotBCTrans');
plt.savefig('bc_sample_day_wMat.png', bbox_inches='tight') 

#making trade volume vs day plots by market
trans=.7  #edgecolor='none'
plt.figure(figsize=(12, 15))
for j, i in enumerate(np.unique(dataset.ProductType)):
    subset=dataset.loc[dataset.ProductType==i]
    uCols=np.unique(subset.ProductName)
    labs=[np.unique(subset.ProductName).tolist().index(k) for k in subset.ProductName]
    plt.subplot(3,2,j+1);
    plt.subplots_adjust(hspace=.3);
    plt.subplots_adjust(wspace=.5);
    plt.scatter(subset[['Day']], subset[['TradeTotBCTrans']], c=labs, cmap=cm.rainbow, alpha=trans); plt.xlabel('Day'); plt.ylabel('TradeTotBCTrans');
    plt.title(i);

    cust_hand=[]
    for j in range(len(uCols)):
        cust_hand.append(mpatches.Patch(color=cm.rainbow(np.linspace(0, 1, len(uCols))[j], alpha=trans), label=uCols[j]))
    plt.legend(handles=cust_hand, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.savefig('agr_scatter_transMat.png', bbox_inches='tight')    

#making trade volume vs time to maturity plots by market
trans=.6  #edgecolor='none'
plt.figure(figsize=(15, 17)) 
for i, j in enumerate(np.unique(dataset.ProductType)):
    subset=dataset.loc[dataset.ProductType==j]
    uCols=np.unique(subset.ProductName)
    labs=[np.unique(subset.ProductName).tolist().index(k) for k in subset.ProductName]
    plt.subplot(3,2,i+1);
    plt.subplots_adjust(hspace=.3);
    plt.subplots_adjust(wspace=.5);
    plt.scatter(subset[['TimeToMaturity']], subset[['TradeTotBCTrans']], c=labs, cmap=cm.rainbow, alpha=trans); plt.xlabel('TimeToMaturity'); 
    plt.ylabel('TradeTotBCTrans'); plt.title(j);
    
    cust_hand=[]
    for j in range(len(uCols)):
        cust_hand.append(mpatches.Patch(color=cm.rainbow(np.linspace(0, 1, len(uCols))[j], alpha=trans), label=uCols[j]))
    plt.legend(handles=cust_hand, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.savefig('types_time_to_mat.png', bbox_inches='tight')



