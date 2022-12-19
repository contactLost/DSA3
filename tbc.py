from datetime import datetime
from multiprocessing.connection import wait
import channel as channel
import os
import sys
import Node
import constants
NP = constants.NP = int(sys.argv[1]) #num of processes
MINT = constants.MINT = int(sys.argv[2]) #miliseconds
MAXT = constants.MAXT = int(sys.argv[3]) #miliseconds
AVGT = constants.AVGT = int(sys.argv[4]) #miliseconds
NR = constants.NR = int(sys.argv[5]) #num of requests
#Flush Redis
chan = channel.Channel()
chan.channel.flushall()

nodes = [Node.Node() for i in range(int(NP))]

for i in range(int(NP)):
    pid = os.fork()
    if pid == 0:
        nodes[i].run()
        os._exit(0)

