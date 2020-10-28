AD HOC Simulation Notes

Two main functions:
# broadcast(): node i writes the message and broadcast
# send(): node i sends (either its own message or a message it received from other nodes) to another node

Important settings (adjustable):
1. BROADCAST_DURATION = 5 days: random phones are chosen to broadcast messages during BROADCAST_DURATION
2. MAX_DELAY = 1 day: a message is considered dropped after MAX_DELAY
3. BROADCAST_INTERVAL = 1 hour: every 1 hour, the program selects (NUM_BROADCAST, see next setting) number of broadcasters
4. NUM_BROADCAST = 3 (To be more realistic: use a random function or use a t dependent number, ie. more messages during day and fewer during evening)
5. WAKE_INTERVAL = 10 min: every node wakes up every 10 minute to send/receive a message (this does not interfere with broadcast)
6. END_ONLINE = 30 min: all nodes go online sometime between t=0 and t=30 min (this setting gives each node a different wakeup schedule)
7. PERCENT_NODES_USED = 1: selects a subset of the contact trace dataset by selecting some percentage of the nodes (floor); 1 means all data is selected

Model assumptions about the network:
1. ASSUMPTION: Messages do not jump more than once at t; This is because we cannot add to dictionary while looping over it
	TODO: add a loop at the end of t to do chained jumps
2. ASSUMPTION: Phone can only send and receive messages if it's awake (every 10 min); but it can broadcast a message anytime as long as it is online (all phones go online at the beginning and remain online during the simulation)
3. ASSUMPTION: If the receiver has received the message already, it will receive that same message again when some node sends it back. This means the message will stay in the air longer (ie. timeR is updated), 
		but this transaction won't be considered in calculating the distribution and mean of delay  
4. ASSUMPTION: When a node is selected to broadcast, it keeps broadcasting (broadcast()) the message every wake_interval until max_relay is reached
5. ASSUMPTION: When a node receives a message, it keeps looking for someone to send (send()) the message every wake_interval until max_relay is reached

OTHER TODOS:
1. Check aforementioned assumptions and correct any that leads to bias
2. Investigate the ONE simulator; adjust metrics to produce a trace dataset that better mimics a university setting