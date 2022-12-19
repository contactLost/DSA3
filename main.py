from datetime import datetime
from multiprocessing.connection import wait
import channel as channel
import os
import sys
import RingNode
import constants

NP = 10 # sys.argv[1]
DATAFILE = sys.argv[2]
DELTA = sys.argv[3]
TOTCOUNT = sys.argv[4]
LOGFILE = sys.argv[5]
MAXTIME = sys.argv[6]

constants.NP = int(NP)
constants.DATAFILE = DATAFILE
constants.DELTA = int(DELTA)
constants.TOTCOUNT = int(TOTCOUNT)
constants.LOGFILE = LOGFILE
constants.MAXTIME = int(MAXTIME)

starttime = datetime.utcnow()

chan = channel.Channel()
chan.channel.flushall()

f = open(DATAFILE ,"wt")
f.write("0\n0")
f.close()

f = open(LOGFILE ,"wt")
f.write("")
f.close()

nodes = [RingNode.RingNode(starttime) for i in range(int(NP))]
[nodes[i].getTopology() for i in range(int(NP))]
chan.changeTokenHolder(nodes[0].nodeID)
chan.startProgram()

for i in range(int(NP)):
    pid = os.fork()
    if pid == 0:
        nodes[i].run()
        os._exit(0)


