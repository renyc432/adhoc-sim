# -*- coding: utf-8 -*-

import pandas as pd
#import numpy as np
import os
import random
import math
#from collections import deque
#from statistics import mean

os.chdir('C:\\Users\\rs\\Desktop\\Research\\MDP\\VIP Freespeech\\Simulation\\Sim')
contacts = pd.read_csv('contacts.csv')

###########################################
#############  SIMULATION  ################
###########################################
# start timestamp; change this variable depending on the dataset
START = 0
# run simulation for 7 days, stop broadcasting after that
BROADCAST_DURATION = 1 * 2 * 3600
# drop a message 2 days after broadcasted or anyone has received it
MAX_DELAY = 1 * 1 * 3600
# broadcast every 1 hour
BROADCAST_INTERVAL = 60*60
# number of broadcasting nodes
NUM_BROADCAST = 1

# TODO: nodes send messages every 10 minutes; nodes send each message 10 times upon receival
#       Current version: nodes send a message as long as there is a receiver no matter the time
SEND_INTERVAL = 10 * 60
SEND_FREQUENCY = 10 

# nodes wake up to receive messages every 5 minutes
RECEIVE_INTERVAL = 5 * 60
# All phones go online sometime between START and START+END_ONLINE (1h)
# This variable is used to create a different receiving schedule for every node
END_ONLINE = 30*60

# Phones record the time each node goes online; it ranges from [START, START+60*60]
# The phone then starts receiving messages every RECEIVE_INTERVAL and can be selected to broadcast
# This schedule is randomly selected; 
# NOTE: the delay/drop rates for different schedules should be tested
#       Previous runs have shown if all nodes share the same receive schedule, 
#       then the delivery delay decreases and drop rate decreases
random.seed(425234)
phones = {'PID': list(range(0,36)),
         'timeOnline': random.sample(range(START,START+END_ONLINE+1),36)}
#DEBUG
#phones = {'PID': list(range(0,36)),
#          'timeOnline': [0]*36}
phones = pd.DataFrame(phones)

# messages
# unque to each broadcasted message
class Message:
    MID = 0
    broadcaster = 0
    timeBroadcasted = 0
    # TODO: check whether path[] is necessary
    path = []

#    timeReceived = []
    
    def __init__(self, MID_in, b_in, timeB_in):
        self.MID = MID_in
        self.broadcaster = b_in
        self.timeBroadcasted = timeB_in
        self.path = [b_in]
#        self.timeBroadcasted = tB_in
#        self.timeReceived = tR_in


# Keep for reference
# messages in the air
# =============================================================================
# class Message_ITA:
#     MID = 0
#     holder = 0
#     timeReceived = 0
#     
#     def __init__(self, MID_in, h_in, tR_in):
#         self.MID = MID_in
#         self.holder = h_in
#         self.timeReceived = tR_in
# =============================================================================
    
# Generates message ID (MID)
MID_counter = 0

# messages broadcasted
messages = []

# messages received
transactions = pd.DataFrame(columns=['MID','receiver',
                                     'timeBroadcasted','timeReceived'])

# NOTE: if NUM_BROADCAST changes every t, this global variable is needed
# total_messages = 0

# This dataframe would take up more memory, but could potentially speed up the simulation
messages_ITA = pd.DataFrame(columns=['MID','receiver','timeReceived'])


def broadcast(broadcaster, timeB):
    global MID_counter
    global messages
    
    
    # ASSUMPTION: In this simulation, we assume node only broadcasts once, 
    # received only if someone is receiving, dropped otherwise
    
    # TODO: this is not right, if no one is receiving, add them to messages_ITA
    
    
    #DEBUG
    #if timeB % RECEIVE_INTERVAL != 0:
    #    return
    
    # Search for nodes in contact with the broadcaster at timeB
    receivers = contacts[((contacts['node1'] == broadcaster) 
                    | (contacts['node2'] == broadcaster))
                    & ((contacts['start'] <= timeB)
                    & (contacts['end'] >= timeB))]
    
    messages.append(Message(MID_counter, broadcaster, timeB))


    # For all receivers, call send(), timeB is the receive time
    if not(receivers.empty):
        for index, receiver in receivers.iterrows():
                        
            if receiver['node1'] == broadcaster:
                
                #DEBUG
                #print("receiver is", receiver)
                #print("broadcaster is", broadcaster)
                
                # Check the receiver is online AND receive interval time for the receiver is met
                timeOnline = phones[phones['PID']==receiver['node2']]['timeOnline']
                timeOnline = timeOnline.tolist()[0]
                if ((timeOnline <= timeB) and ((timeB-timeOnline) % RECEIVE_INTERVAL == 0)):
                    send(MID_counter, receiver['node2'], timeB)
            else:
                # Check the receiver is online AND receive interval time for the receiver is met
                timeOnline = phones[phones['PID']==receiver['node1']]['timeOnline']
                timeOnline = timeOnline.tolist()[0]
                if ((timeOnline <= timeB) and ((timeB-timeOnline) % RECEIVE_INTERVAL == 0)):
                    send(MID_counter, receiver['node1'], timeB)
    else:
        # ASSUMPTION: If no one receives the message, append to messages_ITA
        #               Equivalently, this means keep broadcasting until MAX_DELAY is met
        # This assumption slows down the operation by so much, it doesn't seem practical anymore
        # TODO: What if we assume a node only sends/broadcasts when receive time is up
        
        
        # BUG: this is not recorded in transaction, so when the broadcaster received
        #       the message back from other nodes, it will be added to the ITA
        # TODO: FIX BUG
        
        # This method of append is incredibly slow, consider a different data structure;
        # such as a list to store all MID and use a different structure to append
        # maybe dictionary key = (MID,receiver); or 2D list; or a list of objects
        
        messages_ITA.loc[len(messages_ITA)] = [MID_counter, broadcaster, timeB]
    MID_counter = MID_counter + 1
    # if NUM_BROADCAST changes every t, this global variable needs to be updated
    # total_messages = total_messages+1
    return

@profile
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
    if(transactions[(transactions['MID'] == MID)
                    & (transactions['receiver'] == receiver)].empty):
        transactions.loc[len(transactions)] = [MID, receiver, timeB, timeR]
        messages_ITA.loc[len(messages_ITA)] = [MID, receiver, timeR]
        messages[MID].path.append(receiver)
    else:
        
        # This is the biggest issue with this code; this takes half of the run time
        messages_ITA.loc[(messages_ITA['MID'] == MID)
                     & (messages_ITA['receiver'] == receiver),'timeReceived'] = timeR
    return

@profile
def main():
    global messages
    global messages_ITA

    for t in range(START, BROADCAST_DURATION+MAX_DELAY+1):
        if t <= START+BROADCAST_DURATION:
            
            # Broadcast, select NUM_BROADCAST nodes from available nodes, call broadcast()
            if t % BROADCAST_INTERVAL == 0:
                if (t <= START+END_ONLINE):
                    phoneAvail = phones[t>=phones['timeOnline']]['PID'].tolist()
                    if (len(phoneAvail) > 0):
                        broadcasters = random.sample(phoneAvail,NUM_BROADCAST)
                    else:
                        broadcasters = []
                else:
                    broadcasters = random.sample(range(0,36),NUM_BROADCAST)
                
                if (len(broadcasters) > 0):
                    for broadcaster in broadcasters:
                    ####################### DEBUG
                    # if t == 0:
                    #     broadcaster = 14
                    ######################
                        broadcast(broadcaster, t)
        
        # At each t, update messages_ITA
        # Drop messages past MAX_DELAY since timeReceived
        messages_ITA = messages_ITA[messages_ITA['timeReceived'] + MAX_DELAY >= t]
        
        # ATERNATIVE data structure: filtering for m_ITA list structure
        #messages_ITA_new = [m for m in messages_ITA if (m.timeReceived + MAX_DELAY) >= t]
        #messages_ITA = messages_ITA_new
        
        # Nodes wake up to receive messages every 5 minutes
        # TODO: create a customized send schedule for all nodes
        #   ie. assign a custom starting time
        
        # if t % RECEIVE_INTERVAL != 0:
        #     continue
        
        # if not empty
        if not(messages_ITA.empty):
            for index, m in messages_ITA.iterrows():
            #for m in messages_ITA:
                           
                # ASSUMPTION: In this simulation,
                #               we assume nodes send messages all the time                
                
                # ASSUMPTION: In this simulation, 
                #               we assume nodes are able to send/relay messages 
                #               at same t as when they are received
                
                sender = m['receiver']

                # TODO: Optimize: 1. combine conditionals:https://datascience.stackexchange.com/questions/23264/improve-pandas-dataframe-filtering-speed
                #                   2. create a duplicate of contacts, except switching places node1 and node2
                #                      This will reduce search time, though may create problem at other parts of the code
                receivers = contacts[((contacts['node1'] == sender) 
                    | (contacts['node2'] == sender))
                    & ((contacts['start'] <= t)
                    & (contacts['end'] >= t))]
                
                #if not empty
                if not(receivers.empty):
                    for index, receiver in receivers.iterrows():                                                                           
                        if receiver['node1'] == sender:                            
                            send(m['MID'], receiver['node2'], t)
                        else:
                            send(m['MID'], receiver['node1'], t)
                            
        print("The time is", t)
        
    
    if (len(transactions.index) == 0):
        delay_mean = "No successfully broadcasted messages"
        drop_rate = 1
        return ([delay_mean, drop_rate])
 
    # Calculate average delivery delay
    delay_mean = sum(transactions['timeReceived'] - transactions['timeBroadcasted'])/len(transactions.index)
    
    # Calculate drop rate
    # NOTE: count the total number of messages broadcasted differently if NUM_BROADCAST changes every t
    messages_total = math.floor(BROADCAST_DURATION / BROADCAST_INTERVAL) * NUM_BROADCAST + 1
    messages_success = len(transactions.MID.unique())
    print("Number of total messages broadcasted: ", messages_total)
    print("Number of successful messages broadcasted: ", messages_success)
    drop_rate = (messages_total - messages_success) / messages_total
    return ([delay_mean, drop_rate])

delay_mean = main()
print(delay_mean)



#x= deque()
# =============================================================================
# x = random.sample(range(0,35),NUM_BROADCAST)
# for y in x:
#     print(y)
# =============================================================================
