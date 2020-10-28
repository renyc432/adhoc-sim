# This module contains: broadcast()
# broadcast() initiates a message, ie. node i writes the message and broadcast; 

import setting as st
from message import Message
from send_message import send


#@profile
def broadcast(contacts_grouped, phones, messages, messages_ITA, transactions, MID_counter, broadcaster, timeB):
     
    # ASSUMPTION: When a node is selected to broadcast, it keeps broadcasting the message
    #               every interval until max_relay is reached   
    
    # Search for nodes in contact with the broadcaster at timeB
    b_trace = contacts_grouped[broadcaster]
    receivers = b_trace[(b_trace['start'] <= timeB)
                        & (b_trace['end'] >= timeB)]
    
    messages.append(Message(MID_counter, broadcaster, timeB))


    # For all receivers, call send(), timeB is the receive time
    # If no receivers, push to messages_ITA
    if not(receivers.empty):
        for index, receiver in receivers.iterrows():
                        
            if receiver['node1'] == broadcaster:
                
                # Check the receiver is online (<= timeB) 
                # AND receive interval time for the receiver is met
                timeOnline = phones[receiver['node2']]

                if ((timeOnline <= timeB) and ((timeB-timeOnline) % st.WAKE_INTERVAL == 0)):
                    send(messages, messages_ITA, transactions, MID_counter, receiver['node2'], timeB)
                else: 
                    # if receiver not online yet, push message to messages_ITA
                    messages_ITA[MID_counter, broadcaster] = timeB
            else:
                # Check whether the receiver is online AND whether it is receiver's wake interval time
                timeOnline = phones[receiver['node1']]
                
                if ((timeOnline <= timeB) and ((timeB-timeOnline) % st.WAKE_INTERVAL == 0)):
                    send(messages, messages_ITA, transactions, MID_counter, receiver['node1'], timeB)
                else:
                    # if receiver not online yet, push message to messages_ITA
                    messages_ITA[MID_counter, broadcaster] = timeB
    else:
        # ASSUMPTION: If no one receives the message, append to messages_ITA
        #               Equivalently, this means keep broadcasting until MAX_DELAY is met
        # This assumption slows down the operation by so much        
        messages_ITA[MID_counter, broadcaster] = timeB
        
    return