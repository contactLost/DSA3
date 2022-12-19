import os
import channel
import random
import time
import constants
import threading
import Req
import LogicalClock

import datetime

lock = threading.Lock()


class Node:
    def __init__(self):
        self.ci = channel.Channel()
        successfulInit = False
        self.nodeID = ""
        self.logicalClock = LogicalClock.LogicalClock()
        self.inboundREQs = []
        self.inboundACKs = []
        self.orderedQueue = []
        self.deliveredMSGs = []
        self.allMessagesProcessed = False
        self.deliveredMSGAmount = 0
        self.req_count = 1

        while not successfulInit:
            try:
                self.nodeID = self.ci.join("ring1")
                successfulInit = True
            except(AssertionError):
                None


    def get_ack_time(self, ackStr):
        return ackStr.split(",")[1]

    def listenRequests(self):
        while not self.checkFinished():
            lock.acquire()
            # Listen to requests
            message = None
            message = self.ci.recvFromAny(3)

            #When a request received
            if (not message == None) and message[0:3] == constants.REQ_WORD:
                reqObj = self.get_req_obj(message[1])
                self.logicalClock.updateClock(reqObj.time)
                self.inboundREQs.append(reqObj)
                print(message)
            
            #When a ack received
            elif (not message == None) and message[0:3] == constants.ACK_WORD:
                ack = message[1]
                self.logicalClock.updateClock(self.get_ack_time(ack))
                self.inboundACKs.append(ack)
            lock.release()

    def sendACKs(self, request):
        ack = constants.ACK_WORD + "," + str(self.logicalClock.getClock()) + "," + request.get_request_data()
        self.ci.sendToAll(ack)
        self.logicalClock.increaseClock()

    def broadcast_thread(self):
        while True:
            random_t = -1
            current_time = datetime.datetime.now().timestamp()
            random.seed(current_time + float(self.nodeID))
            is_end = True
            print('brad cast brom')
            while is_end:
                print('here')
                lam = 1 / constants.AVGT

                random_t = int(random.expovariate(lam))
                print(constants.MAXT > random_t > constants.MINT)
                if constants.MAXT > random_t > constants.MINT:
                    is_end = False
                    print('end')

            print('random_t ' + str(random_t))
            time.sleep(random_t / 1000)
            current_time = datetime.datetime.now().timestamp()
            self.ci.sendToAll(
                str(constants.REQ_WORD) + ',' + str(self.nodeID) + ',' + str(current_time) + ',' + str(self.req_no))
            self.req_no += self.req_no

            if self.req_no >= constants.NR:
                break

    def order_manager_thread(self):
        while not self.checkFinished():
            lock.acquire()

            # Empty Inbound Reqs
            while not self.inboundREQs.count == 0:
                request = self.inboundREQs.pop()
                for i in range(len(self.orderedQueue)):
                    req_i = self.orderedQueue[i]
                    if req_i.time > request.time:
                        self.orderedQueue.insert(i, request)
                        # Send Ack
                        self.sendACKs(request)
                        break
                    elif req_i.time == request.time:
                        if int(req_i.sender) > int(request.sender):
                            self.orderedQueue.insert(i, request)
                            # Send Ack
                            self.sendACKs(request)
                            break

                        #Last Request
                        elif (i + 1 == (self.orderedQueue.count)) or (not self.orderedQueue[i + 1].time == request.time):
                            self.orderedQueue.insert(i + 1, request)
                            # Send Ack
                            self.sendACKs(request)
                            break
                    
            #Empty Acks
            i = 0
            while i < len(self.inboundACKs):
                ack = self.inboundACKs[i]
                for req in self.orderedQueue:
                    if req.ackRequest(ack):
                        self.inboundACKs.remove(i)
                        i = i - 1
                i = i + 1

            #Check If Delivarable
            if self.orderedQueue[0].is_request_acked_by_everyone():
                msg = self.orderedQueue.pop()
                self.deliveredMSGs.append(msg)
                self.deliveredMSGAmount = self.deliveredMSGAmount + 1
            lock.release()

    def get_req_obj(self, reqString) -> Req.Req:
        data = reqString.split(",")
        reqObj = Req.Req(data[1], int(data[2]), int(data[3]), reqString)
        return reqObj

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
        print(self.inboundREQs)

    def writeToFile(self):

        pid = str(self.nodeID)
        ospid = str(os.getpid())  # If write to file is run on a thread this line might cause some problems
        reqid = "001"  # To be figured out later TODO
        ts = ("0001:" + str(self.nodeID))
        rt = datetime.datetime.now().timestamp()

        writeToWrite = "pid=" + pid + ", ospid=" + ospid + ", reqid=" + reqid + ", ts=" + ts + ", rt=" + str(rt) + "\n"

        # open file
        filename = str(self.nodeID) + ".txt"

        if os.path.exists(filename):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not
        print("select ", append_write)
        f = open(filename, append_write, )

        f.write(writeToWrite)
        print(writeToWrite)
        f.close()

    def checkFinished(self):
        if self.deliveredMSGs.count == 0 and self.deliveredMSGAmount == constants.NR * constants.NP:
            return True
        return False
