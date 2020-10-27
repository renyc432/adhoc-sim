# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import random
import math
from datetime import datetime
import pymysql
import sys

#from statistics import mean

path = 'C:\\Users\\roy79\\Desktop\\Research\\adhoc-sim'
os.chdir(path)
contacts = pd.read_csv('contacts.csv')

###########################################
#############  SIMULATION  ################
###########################################
# start timestamp; change this variable depending on the dataset
START = 0
# run simulation for 7 days, stop broadcasting after that
BROADCAST_DURATION = 5 * 24 * 3600
# drop a message 2 days after broadcasted or anyone has received it
MAX_DELAY = 1 * 24 * 3600
# broadcast every 1 hour
BROADCAST_INTERVAL = 60*60
# number of broadcasting nodes
NUM_BROADCAST = 3

# nodes wake up to receive messages every 5 minutes
RECEIVE_INTERVAL = 10 * 60
# All phones go online sometime between START and START+END_ONLINE (1h)
# This variable is used to create a different receiving schedule for every node
END_ONLINE = 30*60

#PERCENT_NODES = 0.80


# Phones record the time each node goes online; it ranges from [START, START+60*60]
# The phone then starts receiving messages every RECEIVE_INTERVAL and can be selected to broadcast
# This schedule is randomly selected; 
# NOTE: the delay/drop rates for different schedules should be tested
#       Previous runs have shown if all nodes share the same receive schedule, 
#       then the delivery delay decreases and drop rate decreases

PID = np.concatenate((contacts['node1'].unique(),contacts['node2'].unique()))
PID = np.unique(PID)
NUMBER_OF_PHONE = len(PID)
PID = list(range(0,NUMBER_OF_PHONE))
random.seed(425234)
timeOnline = random.sample(range(START,START+END_ONLINE+1),NUMBER_OF_PHONE)  
#timeOnline = [0]*36  
phones = dict(zip(PID,timeOnline))


# messages
# unque to each broadcasted message
class Message:
    MID = 0
    broadcaster = 0
    timeBroadcasted = 0
    # TODO: check whether path[] is necessary
    path = []
    
    def __init__(self, MID_in, b_in, timeB_in):
        self.MID = MID_in
        self.broadcaster = b_in
        self.timeBroadcasted = timeB_in
        self.path = [b_in]

# Generates message ID (MID)
MID_counter = 0

# messages broadcasted
messages = []

# messages received
# {[MID,receiver] : timeR - timeB}
transactions = {}

# {[MID,receiver] : timeR}
messages_ITA = {}

# SQL settings
hostname = 'localhost'
username = 'root'
password = 'rootroot'
database = 'cambridge_students'


#@profile
def broadcast(broadcaster, timeB):
    global MID_counter
    global messages
    
    
    # ASSUMPTION: When a node is selected to broadcast, it keeps broadcasting the message
    #               every interval until max_relay is reached   
    
    # Search for nodes in contact with the broadcaster at timeB
    receivers = contacts[((contacts['node1'] == broadcaster) 
                    | (contacts['node2'] == broadcaster))
                    & ((contacts['start'] <= timeB)
                    & (contacts['end'] >= timeB))]
    
    messages.append(Message(MID_counter, broadcaster, timeB))


    # For all receivers, call send(), timeB is the receive time
    # If no receivers, push to messages_ITA
    if not(receivers.empty):
        for index, receiver in receivers.iterrows():
                        
            if receiver['node1'] == broadcaster:
                
                # Check the receiver is online (<= timeB) 
                # AND receive interval time for the receiver is met
                timeOnline = phones[receiver['node2']]

                if ((timeOnline <= timeB) and ((timeB-timeOnline) % RECEIVE_INTERVAL == 0)):
                    send(MID_counter, receiver['node2'], timeB)
                else: 
                    # if receiver not online yet, push message to messages_ITA
                    messages_ITA[MID_counter, broadcaster] = timeB
            else:
                # Check the receiver is online AND receive interval time for the receiver is met
                timeOnline = phones[receiver['node1']]
                
                if ((timeOnline <= timeB) and ((timeB-timeOnline) % RECEIVE_INTERVAL == 0)):
                    send(MID_counter, receiver['node1'], timeB)
                else:
                    # if receiver not online yet, push message to messages_ITA
                    messages_ITA[MID_counter, broadcaster] = timeB
    else:
        # ASSUMPTION: If no one receives the message, append to messages_ITA
        #               Equivalently, this means keep broadcasting until MAX_DELAY is met
        # This assumption slows down the operation by so much        
        messages_ITA[MID_counter, broadcaster] = timeB
        
        
    MID_counter = MID_counter + 1
    return

#@profile
def send(MID, receiver, timeR):
    global messages
    global messages_ITA
    global transactions       
    
    timeB = messages[MID].timeBroadcasted
    
    # ASSUMPTION: if the message has been transacted between A and B
    #   in the last X minutes, then the message won't be transacted again
    #   This will reduce the size of message_ITA significantly
    #   This is dealt by the current structure of code (same 10 minute receive interval)
    
    # ASSUMPTION: if the receiver has received the message already,  
    #    it will receive that same message again,
    #    but it won't be recorded as a transaction
    #    It will update timeReceived into message_ITA 
    
    # if MID and the receiver are in transaction, then update m_ITA['timeReceived']
    # else, append new entry to transaction and m_ITA
        
    if((MID,receiver) not in transactions):
        transactions[MID,receiver] = timeR-timeB
        messages_ITA[MID,receiver] = timeR        
        messages[MID].path.append(receiver)
    else:
        messages_ITA[MID,receiver] = timeR        
    return


def SQLconnect(hostname, username, password, database):
    try:
        db = pymysql.connect(hostname, username, password, database)
        print('Connection to SQL server successfully established')
        return db
    except:
        print('ERROR: SQL server connection failed')

def SQLquery(db, query):
    try:
        receivers = pd.read_sql(query,db)
                
        return receivers
    except:
        sys.exit('ERROR: SQL query failed')

def SQLdisconnect(db):
    db.close()
    print('SQL server has been disconnected')



def table_split(df, col):
    grouped = df.groupby(col)
    return grouped

# Define a function to select percentage number of nodes in contact traces
#def node_select(percentage):
    


#@profile
def main():
    global messages
    global messages_ITA

    time_begin = datetime.now()
    
    
    # Setup
        
    
    #node_select(PERCENT_NODES)
    
    
    
    
    # connect to SQL server
    #db = SQLconnect(hostname, username, password, database)
    
    # split dataset for faster select
    grouped_node1 = table_split(contacts, 'node1')
    grouped_node2 = table_split(contacts, 'node2')

    grouped_node1_keys = grouped_node1.groups.keys()
    grouped_node2_keys = grouped_node2.groups.keys()
    
    contacts_grouped = {}
    
    for i in list(range(0,NUMBER_OF_PHONE)):
        if (i in grouped_node1_keys):
            node1 = grouped_node1.get_group(i)
            if (i in grouped_node2_keys):
                grouped_sender = pd.concat([node1,grouped_node2.get_group(i)])
            else:
                grouped_sender = node1
        elif (i in grouped_node2_keys):                       
            grouped_sender = grouped_node2.get_group(i)
        else:
            grouped_sender = pd.DataFrame()
        contacts_grouped[i] = grouped_sender


    for t in range(START, BROADCAST_DURATION+MAX_DELAY+1):
        if t <= START+BROADCAST_DURATION:
            
            # Broadcast, select NUM_BROADCAST nodes from available nodes, call broadcast()
            if t % BROADCAST_INTERVAL == 0:
                if (t <= START+END_ONLINE):
                                 
                    phoneAvail = {k:v for k,v in phones.items() if t>=v}.keys()
                    
                    if (len(phoneAvail) > 0):
                        broadcasters = random.sample(phoneAvail,NUM_BROADCAST)
                    else:
                        broadcasters = []
                else:
                    broadcasters = random.sample(range(0,NUMBER_OF_PHONE),NUM_BROADCAST)
                
                if (len(broadcasters) > 0):
                    for broadcaster in broadcasters:
                        broadcast(broadcaster, t)
        
        # At each t, update messages_ITA
        # Drop messages past MAX_DELAY since timeReceived        
        messages_ITA = {k:v for k,v in messages_ITA.items() if v+MAX_DELAY >=t}
        
        
        if bool(messages_ITA):
                            
            # ASSUMPTION: Messages do not jump more than once at t
            #           This is because we cannot add to dictionary while looping over it
            # TODO: add a loop inside the loop to do chained jumps
            
            keys = list(messages_ITA)
            for key in keys:
                                
                sender = key[1]  
                
                # THIS IF statement is the implementation of send_interval
                # ASSUMPTION: Assumes phone sends a messages only if it's awake (RECEIVE_INTERVAL)
                
                if ((t-phones[key[1]])%RECEIVE_INTERVAL == 0):
                    
# =============================================================================
#                     receivers = contacts[((contacts['node1'] == sender) 
#                             | (contacts['node2'] == sender))
#                             & ((contacts['start'] <= t)
#                             & (contacts['end'] >= t))] 
# =============================================================================

                    grouped_sender = contacts_grouped[sender]
                    receivers = grouped_sender[(grouped_sender['start']<=t)
                                               & (grouped_sender['end']>=t)]
                    
# =============================================================================
#                     # Dictionary version of the code
#                     time = datetime.now()
#                     for i in list(range(1,500)):
#                         receivers = contacts[((contacts['node1'] == sender) 
#                             | (contacts['node2'] == sender))
#                             & ((contacts['start'] <= t)
#                             & (contacts['end'] >= t))]                   
#                     timediff = datetime.now()-time
#                     print(timediff)
#                     
#                     # SQL version of the code
#                     time = datetime.now()
#                     for i in list(range(1,500)):
#                         query = 'select * from contacts where (node1 = ' + str(sender) + \
#                             ' or node2 = ' + str(sender) + ' ) and t_start <= ' + str(t) + \
#                             ' and t_end >= ' + str(t) + ';'                        
#                         receivers = SQLquery(db,query)
#                     timediff = datetime.now()-time
#                     print(timediff)
# =============================================================================


                    #if not empty
                    if not(receivers.empty):
                        for index, receiver in receivers.iterrows():                                                                           
                            if receiver['node1'] == sender:                            
                                send(key[0],receiver['node2'],t)
                            else:
                                send(key[0],receiver['node1'],t)                           
        print("The time is", t)
                
    if (not transactions):
        delay_mean = "No successfully broadcasted messages"
        drop_rate = 1
        return ([delay_mean, drop_rate])
 
    
    # Calculate average delivery delay    
    delay_mean = sum(transactions.values())/len(transactions)
    
    # Calculate drop rate
    messages_total = len(messages)
    
    MID_list,receiver_list = zip(*list(messages_ITA))
    messages_success = len(set(MID_list))
    
    print("Number of total messages broadcasted: ", messages_total)
    print("Number of successful messages broadcasted: ", messages_success)
    drop_rate = (messages_total - messages_success) / messages_total
    
    timer = datetime.now()-time_begin
    print('The simulation is a success!!')
    print('This simulation took', timer)
    
    #SQLdisconnect(db);
    
    return ([delay_mean, drop_rate])


## RUN

delay_mean = main()
print(delay_mean)
