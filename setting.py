# Simulation settings

#path = 'C:\\Users\\roy79\\Desktop\\Research\\adhoc-sim'
connection_real = 'cambridge-students.tsv'
connection_synthetic = "cambridge-students-ONE.txt"

contacts_real = 'contacts.csv'
contacts_synthetic = 'contacts_synthetic.csv'

# Start timestamp; change this variable depending on the dataset
START = 0

# A 5+1 day simulation with 100% nodes selected -> completed in ~5 hours depending on the machine
# Initiate for 5 days
INITIATE_DURATION = 5 * 24 * 3600
# Drop a message 1 days after broadcasted or anyone has received it
MAX_DELAY = 1 * 24 * 3600
# Initiate every 1 hour
INITIATE_INTERVAL = 60*60
# Number of initiator nodes every time
NUM_INITIATE = 3


PERCENT_NODES_USED = 1

# how long does it take to transmit messages
#transmit_time = 1

# When a phone sends a message to another phone, 
# there is a 10% chance the message will be successfully received
success_rate = 1


# If True, checks sender/receiver status before transmit
# If False, we assume all phones can send/receive all the time
sender_status_check = True
receiver_status_check = True


# All phones end the day with sleeping for 8 hours, 
# they are in the screenoff state during sleep
DURATION_SLEEP = 8*3600

# During daytime, the phone is in three states
# Each state occupies percent_[state] amount of time (24 hour - DURATION_SLEEP)
percent_foreground = 0.05
percent_background = 0.25
percent_screenoff = 0.7

# When a phone is waken up in the background or screen off, 
# the phone stays in foreground mode for 30 seconds
time_on = 20

# Foreground: the phone receives messages all the time
# Background: the phone receives messages every 1 minute
# Screenoff: the phone receives messages every 2 minute
# Asleep: the phone receives messages every 2 minute
intervals = {1:1, 
             2:1*60,
             3:2*60,
             4:2*60}

# For creating a random schedule for each phone
seed_schedule = 425234

# For selecting a subset of nodes to include in the simulation
seed_nodeselect = 12312

# SQL settings
hostname = 'localhost'
username = 'root'
password = 'rootroot'
database = 'cambridge_students'


