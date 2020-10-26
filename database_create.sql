create database cambridge_students;

create table contacts
(node1 TINYINT NOT NULL,
node2 TINYINT NOT NULL,
t_start INT NOT NULL,
t_end DOUBLE NOT NULL,
PRIMARY KEY(node1,node2,t_start)
);

#filename = 'C:/Users/rs/Desktop/Research/MDP/VIP Freespeech/Simulation/Sim/contacts.csv'

SET GLOBAL local_infile = true;
SHOW GLOBAL VARIABLES LIKE 'local_infile';

load data infile 
'C:/Users/rs/Desktop/Research/MDP/VIP Freespeech/Simulation/Sim/contacts.csv' 
into table contacts 
fields terminated by ',' 
lines terminated by '\n' 
ignore 1 rows
(node1, node2, t_start, t_end);

create index receiver_search on contacts (node1,node2,t_start,t_end);



use cambridge_students;

# #rows = 439017; there are 440000+ rows in the csv; why???
select count(*) from contacts;



select * from contacts where (node1 = 123 or node2 = 123 ) and t_start <= 7200 and t_end >= 7200;