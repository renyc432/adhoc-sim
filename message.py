# messages
# unque to each broadcasted message
class Message:
    MID = 0
    broadcaster = 0
    timeBroadcasted = 0
    
    def __init__(self, MID_in, b_in, timeB_in):
        self.MID = MID_in
        self.broadcaster = b_in
        self.timeBroadcasted = timeB_in