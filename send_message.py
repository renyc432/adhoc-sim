# This module contains: Send()
import random
import setting as st
import numpy as np

#@profile
def send(messages, messages_ITA, transactions, MID, receiver, timeR):    
    
    timeB = messages[MID].timeBroadcasted
    
    # if MID and the receiver are in transaction, then update m_ITA['timeReceived']
    # else, append new entry to transaction and m_ITA
        
    if((MID,receiver) not in transactions):
        sent_success = random.choices([True,False],
                                      [st.success_rate, 1-st.success_rate])
        if (sent_success == True):     
            transactions[MID,receiver] = timeR-timeB
            messages_ITA[MID,receiver] = timeR        
    return


# checks whether the phone is ready to send/receive
def status_check(PID, schedules, t):
    # This calculates which half hour interval it is
    half_hour_index = int(np.floor((t % (24*60*60) / (.5*60*60))))
    # This calculates t mod 30 min
    t_half_hour = t % (.5*60*60)
    # This checks which state (foreground, background, etc.) the phone is in
    state = schedules[PID][half_hour_index]
    # This checks if the phone is awake
    t_int = t_half_hour % st.intervals[state]
    
    return (t_int <= st.time_on)