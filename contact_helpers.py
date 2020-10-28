# This module contains: function for preparing the contact trace dataset for the simulation

import pandas as pd
import numpy as np
import random
import setting as st

def split_by_node(contacts):
    # split dataset for faster select
    grouped_node1 = table_split(contacts, 'node1')
    grouped_node2 = table_split(contacts, 'node2')

    grouped_node1_keys = grouped_node1.groups.keys()
    grouped_node2_keys = grouped_node2.groups.keys()
    
    nodes_selected = set(list(grouped_node1_keys)+list(grouped_node2_keys))
    
    contacts_grouped = {}
    
    for i in nodes_selected:
        if (i in grouped_node1_keys):
            node1 = grouped_node1.get_group(i)
            if (i in grouped_node2_keys):
                grouped_sender = pd.concat([node1,grouped_node2.get_group(i)])
            else:
                grouped_sender = node1
        elif (i in grouped_node2_keys):                       
            grouped_sender = grouped_node2.get_group(i)
        else:
            grouped_sender = pd.DataFrame()
        contacts_grouped[i] = grouped_sender
    return contacts_grouped



def table_split(df, col):
    grouped = df.groupby(col)
    return grouped


# Define a function to select percentage number of nodes in contact traces
def node_select(data, num_phone, select_percentage=1, select_integer=None):
    if (select_integer):
        num_node = select_integer
    else:
        num_node = int(np.floor(num_phone*select_percentage))
    random.seed(st.seed_nodeselect)
    nodes_selected = random.sample(range(0,num_phone), num_node)
    nodes_selected.sort()
    
    data = data[data['node1'].isin(nodes_selected) & data['node2'].isin(nodes_selected)]
    return data
