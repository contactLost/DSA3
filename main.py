from datetime import datetime
from multiprocessing.connection import wait
import channel as channel
import os
import sys
import RingNode
import constants

NP = sys.argv[1]
MINT = sys.argv[2]
MAXT = sys.argv[3]
AVGT = sys.argv[4]
NR = sys.argv[5]

constants.NP = int(NP)
constants.MINT = int(MINT)
constants.MAXT = int(MAXT)
constants.AVGT = int(AVGT)
constants.NR = NR

starttime = datetime.utcnow()

chan = channel.Channel()
chan.channel.flushall()

# f = open(DATAFILE ,"wt")
# f.write("0\n0")
# f.close()

# f = open(LOGFILE ,"wt")
# f.write("")
# f.close()

nodes = [RingNode.RingNode(starttime) for i in range(int(NP))]

for i in range(int(NP)):
    pid = os.fork()
    if pid == 0:
        nodes[i].run()
        os._exit(0)


