# This module contains: Send()

#@profile
def send(messages, messages_ITA, transactions, MID, receiver, timeR):    
    
    timeB = messages[MID].timeBroadcasted
    
    # ASSUMPTION: if the receiver has received the message already,  
    #    it will receive that same message again, ie. the timeReceived will be updated
    #    but it won't be recorded as a transaction
    
    # if MID and the receiver are in transaction, then update m_ITA['timeReceived']
    # else, append new entry to transaction and m_ITA
        
    if((MID,receiver) not in transactions):
        transactions[MID,receiver] = timeR-timeB
        messages_ITA[MID,receiver] = timeR        
    else:
        messages_ITA[MID,receiver] = timeR        
    return