import pandas as pd
import numpy as np
import os
#from statistics import mean
from datetime import datetime
import setting as st

###########################################
##########  CREATE DATABASE  ##############
###########################################

#@profile
def build_contact(connection_file):
    
    time_begin = datetime.now()

    #filename = 'cambridge-students.tsv'
    mydata = pd.read_csv(connection_file,sep='\t')

    #mydata = pd.read_csv(connection_file,delimiter=' ')
    
    mydata_sim = mydata[['time','node1','node2','type']]
    mydata_sim = mydata_sim.assign(time=pd.to_numeric(mydata_sim.loc[:,'time'],downcast='integer'))
    
    # store values in an array
    store = np.array([[1,2,3,4]])
    #DURATION_MEAN = 625
    #Optimize: vectorize??
    for index, row in mydata_sim.iterrows():
        #print(index)
        if row['type']== 'up':
            node1 = row['node1']
            node2 = row['node2']
            start = row['time']
            duration = None
            #end = None
            #print(type(index))
            
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
                    duration = conn_down['time'] - start
            contact = [node1,node2,start,duration]
            store = np.append(store,[contact],axis=0)
            
    
    # Add starting timestamp to all the timestamp to fit the algorithm
    
    contacts = pd.DataFrame(store,columns=['node1','node2','start','duration'])
    
    # take out the first row created as a placeholder
    contacts = contacts.iloc[1:]
    
    #DURATION_MEAN is the average of all valid durations calculated from all up/down pairs
    #   625.0205034741998
    DURATION_MEAN = int(np.floor(np.mean(contacts['duration'])))
    contacts['duration'] = contacts['duration'].fillna(DURATION_MEAN)
    
    contacts['end'] = contacts['start']+contacts['duration']
    
    contacts = contacts[['node1','node2','start','end']]
    contacts.to_csv('contacts.csv',index=False)
    
    timer = datetime.now()-time_begin
    print('This conversion took', timer)


## RUN
build_contact(st.connection_real)

