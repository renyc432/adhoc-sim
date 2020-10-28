
# After testing, I find that SQL is slower than the dictionary approach implemented
# However, I did not further investigate why SQL was slower.
# These functions are kept for future reference


import pandas as pd
import pymysql
import sys
import setting as st

def SQLconnect(host=st.hostname, user=st.username, pwd=st.password, dbase=st.database):
    try:
        db = pymysql.connect(host, user, pwd, dbase)
        print('Connection to SQL server successfully established')
        return db
    except:
        print('ERROR: SQL server connection failed')

def SQLquery(db, query):
    try:
        selected_rows = pd.read_sql(query,db)                
        return selected_rows
    except:
        sys.exit('ERROR: SQL query failed')

def SQLdisconnect(dbase):
    dbase.close()
    print('SQL server has been disconnected')