import os
import channel
import random
import time
import threading


from datetime import datetime

lock = threading.Lock()
class Node:
    def __init__(self):
        self.ci=channel.Channel()
        successfulInit = False
        self.nodeID = ""
        self.inboundMessages = []
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
            self.inboundMessages.append(message)
            print(message)

            lock.release()

    def broadcast_thread(self):
        while not self.checkFinished():
            None

    def order_manager_thread(self):
        while not self.checkFinished():
            None

    def writer_thread(self):
        while not self.checkFinished():
            None




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
