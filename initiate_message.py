# This module contains: initiate()
# initiate() initiates a message, ie. node i writes the message and initiate; 
import setting as st
from message import Message
from send_message import send
from send_message import status_check


#@profile
def initiate(contacts_grouped, schedules, messages, messages_ITA, transactions, MID_counter, initiator, timeB):
     
    # ASSUMPTION: When a node is selected to initiate, it keeps initiating the message
    #               every interval until max_relay is reached   
    
    # Search for nodes in contact with the initiator at timeB
    b_trace = contacts_grouped[initiator]
    receivers = b_trace[(b_trace['start'] <= timeB)
                        & (b_trace['end'] >= timeB)]
    
    messages.append(Message(MID_counter, initiator, timeB))


    # For all receivers, call send(), timeB is the receive time
    # If no receivers, push to messages_ITA
    if not(receivers.empty):
        for index, receiver in receivers.iterrows():
            
            if receiver['node1'] == initiator:                
                if (not st.receiver_status_check) | (status_check(receiver['node2'], schedules, timeB)):
                    send(messages, messages_ITA, transactions, MID_counter, receiver['node2'], timeB)
                else:
                    # if receiver not online yet, push message to messages_ITA
                    messages_ITA[MID_counter, initiator] = timeB

            else:
                if (not st.receiver_status_check) | status_check(receiver['node1'], schedules, timeB):
                    send(messages, messages_ITA, transactions, MID_counter, receiver['node1'], timeB)
                else:
                    # if receiver not online yet, push message to messages_ITA
                    messages_ITA[MID_counter, initiator] = timeB


    else:
        # ASSUMPTION: If no one receives the message, append to messages_ITA
        #               Equivalently, this means keep initiating until MAX_DELAY is met
        # This assumption slows down the operation by so much        
        messages_ITA[MID_counter, initiator] = timeB
        
    return