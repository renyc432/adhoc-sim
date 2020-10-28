import pandas as pd
import numpy as np
import random
from datetime import datetime
import setting as st
from broadcast_message import broadcast
from send_message import send
from contact_helpers import split_by_node
from contact_helpers import node_select


###########################################
#############  SIMULATION  ################
###########################################



#@profile
def run_simulation():
    global messages
    global messages_ITA
    global transactions
    global MID_counter

    time_begin = datetime.now()
    
    
    ############################# Data Preparation ############################
    
    print('Start preparing data for the simulation')
    
    #os.chdir(st.path)
    contacts = pd.read_csv('contacts.csv')
    
    
    # start timestamp; change this variable depending on the dataset
    START = st.START
    # run simulation for 7 days, stop broadcasting after that
    BROADCAST_DURATION = st.BROADCAST_DURATION
    # drop a message 2 days after broadcasted or anyone has received it
    MAX_DELAY = st.MAX_DELAY
    # broadcast every 1 hour
    BROADCAST_INTERVAL = st.BROADCAST_INTERVAL
    # number of broadcasting nodes
    NUM_BROADCAST = st.NUM_BROADCAST
    
    # nodes wake up to receive messages every 5 minutes
    WAKE_INTERVAL = st.WAKE_INTERVAL
    # All phones go online sometime between START and START+END_ONLINE (1h)
    # This variable is used to create a different receiving schedule for every node
    END_ONLINE = st.END_ONLINE
    
    # Phones record the time each node goes online; it ranges from [START, START+60*60]
    # The phone then starts receiving messages every WAKE_INTERVAL and can be selected to broadcast
    # This schedule is randomly selected; 
    # NOTE: the delay/drop rates for different schedules should be tested
    #       Previous runs have shown if all nodes share the same receive schedule, 
    #       then the delivery delay decreases and drop rate decreases
    
    PID = np.concatenate((contacts['node1'].unique(),contacts['node2'].unique()))
    PID = np.unique(PID)
    NUMBER_OF_PHONE = len(PID)
    
    
    # Generates message ID (MID)
    MID_counter = 0
    
    # messages broadcasted
    messages = []
    
    # {[MID,receiver] : timeR}
    messages_ITA = {}
    
    # messages received
    # {[MID,receiver] : timeR - timeB}
    transactions = {}
    
    print('Select a portion (setting.PERCENT_NODES_USED) of contact traces')
    # Subset a group of nodes
    contacts = node_select(contacts, NUMBER_OF_PHONE, st.PERCENT_NODES_USED)
    # Update number of phones in the simulation
    NUMBER_OF_PHONE = int(np.floor(NUMBER_OF_PHONE*st.PERCENT_NODES_USED))
        
    print('Group contact traces by nodes')
    # Split the contact traces by nodes; this provides a speed advantage
    contacts_grouped = split_by_node(contacts)

    
    # Update PID in case only a subset of nodes is used
    PID = list(contacts_grouped.keys())
    random.seed(st.seed_phoneonline)
    timeOnline = random.sample(range(START,START+END_ONLINE+1),NUMBER_OF_PHONE)  
    #timeOnline = [0]*126 
    phones = dict(zip(PID,timeOnline))



    ###########################################################################
        
 
    
    #################### Message Propagation Simulation #######################
    
    print('Start message propagation simulation!!')

    for t in range(START, BROADCAST_DURATION+MAX_DELAY+1):
        if t <= START+BROADCAST_DURATION:
            
            # Broadcast, select NUM_BROADCAST nodes from available nodes, call broadcast()
            if t % BROADCAST_INTERVAL == 0:
                if (t <= START+END_ONLINE):
                                 
                    phoneAvail = {k:v for k,v in phones.items() if t>=v}.keys()
                    
                    if (len(phoneAvail) > 0):
                        broadcasters = random.sample(phoneAvail, NUM_BROADCAST)
                    else:
                        broadcasters = []
                else:
                    broadcasters = random.sample(PID, NUM_BROADCAST)
                
                if (len(broadcasters) > 0):
                    for broadcaster in broadcasters:
                        print (broadcaster)
                        broadcast(contacts_grouped, phones, messages, messages_ITA, transactions, MID_counter, broadcaster, t)
                        MID_counter = MID_counter + 1

        
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
                
                # ASSUMPTION: Phone sends a messages only if it's awake (WAKE_INTERVAL)
                
                if ((t-phones[sender])%WAKE_INTERVAL == 0):
                    
                    grouped_sender = contacts_grouped[sender]
                    receivers = grouped_sender[(grouped_sender['start']<=t)
                                               & (grouped_sender['end']>=t)]

                    #if not empty
                    if not(receivers.empty):
                        for index, receiver in receivers.iterrows():                                                                           
                            if receiver['node1'] == sender:                            
                                send(messages, messages_ITA, transactions, key[0], receiver['node2'], t)
                            else:
                                send(messages, messages_ITA, transactions, key[0], receiver['node1'], t)                           
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


