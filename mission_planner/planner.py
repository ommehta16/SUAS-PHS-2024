import multiprocessing as mp
import multiprocessing.connection
import time

def plan(comm_conn:multiprocessing.connection.Connection, map_conn:multiprocessing.connection.Connection):
    while not comm_conn.poll():
        time.sleep(1)
    f = open('jonathan.orz','+w')

    val = comm_conn.recv()

    f.write(val)

    comm_conn.send("fjkdhsjkhfkasdjh")