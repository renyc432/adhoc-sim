# Simulation settings

#path = 'C:\\Users\\roy79\\Desktop\\Research\\adhoc-sim'

# Start timestamp; change this variable depending on the dataset
START = 0


# A 5+1 day simulation with 100% nodes selected -> completed in ~5 hours depending on the machine
# Broadcast for 5 days
BROADCAST_DURATION = 5 * 24 * 3600
# Drop a message 1 days after broadcasted or anyone has received it
MAX_DELAY = 1 * 24 * 3600
# Broadcast every 1 hour
BROADCAST_INTERVAL = 60*60
# Number of broadcasting nodes every time
NUM_BROADCAST = 3

# Nodes wake up to receive and send messages every 10 minutes
WAKE_INTERVAL = 10 * 60

# All phones go online sometime between START and START+END_ONLINE (1h)
# This variable is used to create a different wakeup schedule for every node
END_ONLINE = 30*60

PERCENT_NODES_USED = .8


# SQL settings
hostname = 'localhost'
username = 'root'
password = 'rootroot'
database = 'cambridge_students'


# For selecting a list of time the node goes online
seed_phoneonline = 425234

# For selecting a subset of nodes to include in the simulation
seed_nodeselect = 12312