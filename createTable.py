# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import os
#from statistics import mean

###########################################
##########  CREATE DATABASE  ##############
###########################################

os.chdir('C:\\Users\\rs\\Desktop\\Undergrad\\Research\\MDP\\VIP Freespeech\\Simulation\\Sim')
mydata = pd.read_csv("C:\\Users\\rs\\Desktop\\Undergrad\\Research\\MDP\\VIP Freespeech\\Simulation\\cambridge-students.tsv", sep="\t")

mydata_sim = mydata[['time','node1','node2','type']]

store = np.array([[1,2,3,4]])
#DURATION_MEAN is the average of all valid durations calculated from all up/down pairs
#   625.0205034741998
DURATION_MEAN = 625
#Optimize: vectorize??
for index, row in mydata_sim.iterrows():
    if row['type']== 'up':
        node1 = row['node1']
        node2 = row['node2']
        start = row['time']
        end = start + DURATION_MEAN
        # Find the next node-pair; note: node1 can be found in node2 as well
        conn_down = mydata_sim.loc[(((mydata_sim['node1']==node1) 
                      & (mydata_sim['node2']==node2))
                      | ((mydata_sim['node1']==node2) 
                      & (mydata_sim['node2']==node1)))
                      & (mydata_sim.index > index)]
        #case: if this is the last record of the pair, stop
        if not(conn_down.empty):
            conn_down = conn_down.iloc[0]
            
            #case: if the next match is an "up", then stop (ignore this record and move on)
            #   Possible other options: instead of discarding this record, 
            #   find the average contact duration and use this to create an end timestamp
            #   This would increase the number of contacts (8779 -> up to 3724 more)
            #   in reality, 10641 'up' in total, so this option creates 10641 contacts
            
            if conn_down['type'] == 'down':
                end = conn_down['time']
        contact = [node1,node2,start,end]
        store = np.append(store,[contact],axis=0)

# Add starting timestamp to all the timestamp to fit the algorithm

contacts = pd.DataFrame(store,columns=['node1','node2','start','end'])
contacts = contacts.iloc[1:]
contacts['start'] = contacts['start']
contacts['end'] = contacts['end']
#start timestamp: 1130493332

contacts.to_csv('contacts.csv',index=False)



#mydata_sim.loc[mydata_sim['type']=='up']
# mean(contacts['end'] - contacts['start'])

## DEBUG PURPOSE
# =============================================================================
# node1_test = mydata_sim.loc[0,'node1']
# node2_test = mydata_sim.loc[0,'node2']
# index = 0
# 
# test = mydata_sim.loc[((mydata_sim['node1']==node1_test) 
#                       & (mydata_sim['node2']==node2_test))
#                       | ((mydata_sim['node1']==node2_test) 
#                       & (mydata_sim['node2']==node1_test))
#                       & (mydata_sim.index > index)]
# print(not(test.empty))
# test2 = test['type']
# =============================================================================
