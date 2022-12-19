import os
import channel
import random
import time
import constants
import threading
import Req
import LogicalClock


from datetime import datetime

lock = threading.Lock()
class Node:
    def __init__(self):
        self.ci=channel.Channel()
        successfulInit = False
        self.nodeID = ""
        self.logicalClock = LogicalClock.LogicalClock()
        self.inboundMessages = []
        self.inboundACKs = []
        self.orderedQueue = []
        self.deliveredMSGs = []
        self.allMessagesProcessed = False

        while not successfulInit:
            try:
                self.nodeID=self.ci.join("ring1")
                successfulInit = True
            except(AssertionError):
                None
        

    def listenRequests(self):
        while not self.checkFinished():
            lock.acquire()
            #Listen to requests
            message = None
            message = self.ci.recvFromAny(3)

            #When a request received
            if (not message == None) and message[0:4] == constants.REQ_WORD:
                reqObj = self.get_req_obj(message[1])
                self.inboundMessages.append(reqObj)
                print(message)
            
            #When a ack received
            elif (not message == None) and message[0:4] == constants.ACK_WORD:
                None

            lock.release()

    def broadcast_thread(self):
        while not self.checkFinished():
            None

    def order_manager_thread(self):
        while not self.checkFinished():
            lock.acquire()
            #Empty Inbound messages
            while not self.inboundMessages.count == 0:
                request = self.inboundMessages.pop()
                for i in range(len(self.orderedQueue)):
                    req_i = self.orderedQueue[i]
                    if req_i.time > request.time:
                        self.orderedQueue.insert(i, request)
                        #Send Ack
                        break
                    elif req_i.time == request.time:
                        if int(req_i.sender) > int(request.sender):
                            self.orderedQueue.insert(i, request)
                            #Send Ack
                            break
                        
                        if (i + 1 == (self.orderedQueue.count)) or (not self.orderedQueue[i+1].time == request.time):
                            self.orderedQueue.insert(i, request)
                            #Send Ack
                            break
                    
            #Empty Acks


            #Check If Delivarable


            lock.release()


    def writer_thread(self):
        while not self.checkFinished():
            None

    def get_req_obj(self, reqString):
        data = reqString.split(",")
        reqObj = Req.Req(data[1], int(data[2]), int(data[3]), reqString)
        return reqObj

    



    def run(self):
        self.ci.bind(self.nodeID)

        listen_thread = threading.Thread(target=self.listenRequests)
        listen_thread.start()

        broadcast_thread = threading.Thread(target=self.broadcast_thread)
        broadcast_thread.start()

        order_manager_thread = threading.Thread(target=self.order_manager_thread)
        order_manager_thread.start()

        writer_thread = threading.Thread(target=self.writer_thread)
        writer_thread.start()

        self.writeToFile()
        self.ci.sendToAll("Hello From " + self.nodeID)


        listen_thread.join()
        print("Node " + self.nodeID + ": Listen thread exited")
        broadcast_thread.join()
        print("Node " + self.nodeID + ": Broadcast thread exited")
        order_manager_thread.join()
        print("Node " + self.nodeID + ": Order Manager thread exited")
        writer_thread.join()
        print("Node " + self.nodeID + ": Writer thread exited")
        print(self.inboundMessages)
        

    def writeToFile(self):

        pid = str(self.nodeID)
        ospid = str(os.getpid()) #If write to file is run on a thread this line might cause some problems
        reqid = "001"       #To be figured out later TODO
        ts = ("0001:"+str(self.nodeID))
        rt = "no idea"

        writeToWrite = "pid="+pid+", ospid="+ospid+", reqid="+reqid+", ts="+ ts+ ", rt="+rt + "\n"

        #open file
        filename = str(self.nodeID) +".txt"

        if os.path.exists(filename):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        print("select ", append_write)
        f = open(filename, append_write, )

        f.write(writeToWrite)
        print(writeToWrite)
        f.close()
        
    def checkFinished(self):
	    return self.allMessagesProcessed
