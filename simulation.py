import pandas as pd
import numpy as np
import random
from datetime import datetime
import setting as st
from initiate_message import initiate
from send_message import send
from send_message import status_check
from contact_helpers import split_by_node
from contact_helpers import node_select



class Settings_Simulation:  
    def __init__(self, start_in, i_duration_in, max_delay_in, 
                 i_interval_in, num_initiate_in, percent_nodes_in,
                 sender_in, receiver_in):
        self.start = start_in
        self.init_dur = i_duration_in
        self.max_delay = max_delay_in
        self.init_int = i_interval_in
        self.num_init = num_initiate_in
        self.perc_nodes = percent_nodes_in
        self.check_sender = sender_in
        self.check_receiver = receiver_in

def create_schedule(PID, seed):
    
    # Create a 24 hour schedule for each person
    # The 24 hour is divided into half hour intervals
    # There are 4 states.
    # 1 - foreground: app in the foreground
    # 2 - background: app in the background
    # 3 - screenoff: screen off in the pocket
    # 4 - asleep: each phone sleeps for 8 hours at the end of the day
    
    random.seed(seed)

    schedules = {}
    for i in PID:
        schedule_day = random.choices([1,2,3],
                                         k=32,
                                         weights=[st.percent_foreground,
                                                  st.percent_background,
                                                  st.percent_screenoff])
        schedule_ind = schedule_day+[1]*16
        schedules[i] = schedule_ind
    return schedules

# def calc_key_metrics():
    


###########################################
#############  SIMULATION  ################
###########################################

#@profile
def run_simulation(contacts_file):
    global messages
    global messages_ITA
    global transactions
    global MID_counter

    time_begin = datetime.now()
    
    
    ############################# Data Preparation ############################
    
    print('Start preparing data for the simulation')
    
    # Generates message ID (MID)
    MID_counter = 0
    
    # messages initiated
    messages = []
    
    # {[MID,receiver] : timeR}
    messages_ITA = {}
    
    # messages received: {[MID,receiver] : timeR - timeB}
    transactions = {}
    
    set_sim = Settings_Simulation(st.START, st.INITIATE_DURATION, st.MAX_DELAY, 
                       st.INITIATE_INTERVAL, st.NUM_INITIATE, st.PERCENT_NODES_USED,
                       st.sender_status_check, st.receiver_status_check)
    
    contacts = pd.read_csv(contacts_file)
    
    # NOTE: the delay/drop rates for different schedules should be tested
    #       Previous runs have shown if all nodes share the same receive schedule, 
    #       then the delivery delay decreases and drop rate decreases
    
    PID = np.concatenate((contacts['node1'].unique(),contacts['node2'].unique()))
    PID = np.unique(PID)
    num_phone_total = len(PID)

    print('Select a portion (setting.PERCENT_NODES_USED) of contact traces')
    # Subset a group of nodes
    contacts = node_select(contacts, num_phone_total, set_sim.perc_nodes)
    num_phone_chosen = int(np.floor(num_phone_total*set_sim.perc_nodes))
        
    print('Group contact traces by nodes')
    # Split the contact traces by nodes; this provides a speed advantage
    contacts_grouped = split_by_node(contacts)

    # Update PID, necessary when only a subset of nodes is used
    PID = list(contacts_grouped.keys())
    
    schedules = create_schedule(PID, st.seed_schedule)

        

    ###########################################################################
        
 
    
    #################### Message Propagation Simulation #######################
    
    print('Start message propagation simulation!!')

    for t in range(set_sim.start, set_sim.init_dur + set_sim.max_delay + 1):
        if t <= set_sim.start+set_sim.init_dur:
            
            # Initiate, select NUM_INITIATE nodes from available nodes, call initiate()
            if t % set_sim.init_int == 0:
                # It's entirely possible that no one is nearby to receive the message
                initiators = random.sample(PID, set_sim.num_init)
                
                if (len(initiators) > 0):
                    for initiator in initiators:
                        initiate(contacts_grouped, 
                                  schedules, 
                                  messages, 
                                  messages_ITA, 
                                  transactions, 
                                  MID_counter, 
                                  initiator, 
                                  t)
                        MID_counter = MID_counter + 1

        
        # At each t, update messages_ITA
        # Drop messages past MAX_DELAY since timeReceived        
        messages_ITA = {k:v for k,v in messages_ITA.items() if v+set_sim.max_delay >=t}
        
        
        if bool(messages_ITA):
                            
            # ASSUMPTION: Messages do not jump more than once at t
            #           This is because we cannot add to dictionary while looping over it
            # TODO: add a loop inside the loop to do chained jumps
            
            keys = list(messages_ITA)
            for key in keys:                
                sender = key[1]
                
                # If check_sender/check_receiver is False, the message can be sent all the time
                # If True, then check phone status
                if (not set_sim.check_sender) | (status_check(sender, schedules, t)):
                    grouped_sender = contacts_grouped[sender]
                    receivers = grouped_sender[(grouped_sender['start']<=t)
                                               & (grouped_sender['end']>=t)]

                    #if not empty
                    if not(receivers.empty):
                        for index, receiver in receivers.iterrows():
                            
                            if receiver['node1'] == sender:
                                if (not set_sim.check_receiver) | status_check(receiver['node2'], schedules, t):
                                    send(messages, 
                                         messages_ITA, 
                                         transactions, 
                                         key[0], 
                                         receiver['node2'], t)
                            else:
                                if (not set_sim.check_receiver) | status_check(receiver['node1'], schedules, t):
                                    send(messages, 
                                         messages_ITA, 
                                         transactions, 
                                         key[0], 
                                         receiver['node1'], t)                   
        print("The time is", t)
    
    
    ###########################################################################
    
    
    ######################## Key Metrics Calculation ##########################
            
    if (not transactions):
        delay_mean = "No successfully initiated messages"
        drop_rate = 1
        return ([delay_mean, drop_rate])
 
    
    # Calculate average delivery delay    
    delay_mean = sum(transactions.values())/len(transactions)
    
    # Calculate drop rate
    messages_total = len(messages)
    
    MID_list,receiver_list = zip(*list(messages_ITA))
    messages_success = len(set(MID_list))
    
    print("Number of total messages initiated: ", messages_total)
    print("Number of successful messages initiated: ", messages_success)
    drop_rate = (messages_total - messages_success) / messages_total
    
    timer = datetime.now()-time_begin
    print('The simulation is a success!!')
    print('This simulation took', timer)
        
    return ([delay_mean, drop_rate])



