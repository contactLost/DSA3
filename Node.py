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
        self.req_no = 1
        self.received = 0
        self.first = True

        while not successfulInit:
            try:
                self.nodeID = self.ci.join("ring1")
                successfulInit = True
            except(AssertionError):
                None


    def get_ack_time(self, ackStr):
        return int(ackStr.split(",")[1])

    def listenRequests(self):
        while not self.checkFinished():
            # Listen to requests
            message = None
            message = self.ci.recvFromAny(2)
            lock.acquire()

            #When a request received
            if (not message == None) and (message[1][0:3] == constants.REQ_WORD):
                reqObj = self.get_req_obj(message[1])
                self.logicalClock.updateClock(int(reqObj.time))
                self.inboundREQs.append(reqObj)
            
            #When a ack received
            elif (not message == None) and (message[1][0:3] == constants.ACK_WORD):
                ack = message[1]
                self.logicalClock.updateClock(self.get_ack_time(ack))
                self.inboundACKs.append(ack)
            lock.release()

    def sendACKs(self, request):
        ack = constants.ACK_WORD + "," + str(self.logicalClock.getClock()) + "," + request.get_request_data()
        self.ci.sendToAll(ack)
        self.logicalClock.increaseClock()

    def broadcast_thread(self):
        while not self.checkFinished():
            random_t = -1
            current_time = datetime.datetime.now().timestamp()
            random.seed(current_time + float(self.nodeID))
            is_end = True
            while is_end:
                lam = 1 / constants.AVGT

                random_t = int(random.expovariate(lam))
                if constants.MAXT > random_t > constants.MINT:
                    is_end = False

            time.sleep(random_t / 1000)
            self.ci.sendToAll(
                str(constants.REQ_WORD) + ',' + str(self.nodeID) + ',' + str(self.logicalClock.clock) + ',' + str(self.req_no) + ',' + str(datetime.datetime.now().strftime("%H:%M:%S:%f")))
            lock.acquire()
            self.logicalClock.increaseClock()
            self.req_no += 1
            lock.release()
            if self.req_no > constants.NR:
                break

    def order_manager_thread(self):
        while not self.checkFinished():
            time.sleep(1)
            lock.acquire()

            # Empty Inbound Reqs
            while not len(self.inboundREQs) == 0:
                #incoming request
                request = self.inboundREQs.pop(0)

                # Put it into queue
                self.received = self.received + 1
                print(self.received)
                self.orderedQueue.append(request)
                self.orderedQueue.sort(key=lambda x: (x.time, x.sender))

                # Send ACK
                self.sendACKs(request)

            #Empty Acks
            ind = 0
            while ind < len(self.inboundACKs):
                ack = self.inboundACKs[ind]
                for req in self.orderedQueue:
                    if req.ackRequest(ack):
                        self.inboundACKs.pop(ind)
                        ind = ind - 1
                        break
                ind = ind + 1

            #Check If Delivarable
            if len(self.orderedQueue) > 0 and self.orderedQueue[0].is_request_acked_by_everyone():
                msg = self.orderedQueue.pop(0)
                self.deliveredMSGs.append(msg)
                self.deliveredMSGAmount = self.deliveredMSGAmount + 1
            lock.release()

    def get_req_obj(self, reqString) -> Req.Req:
        data = reqString.split(",")
        reqObj = Req.Req(data[1], int(data[2]), int(data[3]), reqString, data[4])
        return reqObj

    def writer_thread(self):
        while not self.checkFinished():
            lock.acquire()
            if len(self.deliveredMSGs) > 0:
                delMSG:Req.Req = self.deliveredMSGs.pop(0) 
                self.writeToFile(delMSG.time,delMSG.reqNo, delMSG.sender, delMSG.realTime)
            lock.release()

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

        listen_thread.join()
        print("Node " + self.nodeID + ": Listen thread exited")
        broadcast_thread.join()
        print("Node " + self.nodeID + ": Broadcast thread exited")
        order_manager_thread.join()
        print("Node " + self.nodeID + ": Order Manager thread exited")
        writer_thread.join()
        print("Node " + self.nodeID + ": Writer thread exited")

    def writeToFile(self,time,reqNo,sender,realtime):
        pid = str(self.nodeID)
        ospid = str(os.getpid())  # If write to file is run on a thread this line might cause some problems
        reqid = reqNo  # To be figured out later TODO
        ts = (str(time)+ ":" + str(sender))
        rt = realtime

        writeToWrite = "pid=" + str(pid) + ", ospid=" + str(ospid) + ", reqid=" + str(reqid) + ", ts=" + str(ts) + ", rt=" + str(rt) + "\n"

        # open file
        filename = str(self.nodeID) + ".txt"

        if not self.first and os.path.exists(filename):
            append_write = 'a'  # append if already exists
        else:
            self.first = False
            append_write = 'w'  # make a new file if not
        f = open(filename, append_write, )

        f.write(writeToWrite)
        print(writeToWrite)
        f.close()

    def checkFinished(self):
        if len(self.deliveredMSGs) == 0 and self.deliveredMSGAmount == constants.NR * constants.NP:
            return True
        return False


    def printOrderedQueue(self):
        if not len(self.orderedQueue) == 0:
            print("Node " + str(self.nodeID) + " Ordered Que -> ")
            for req in self.orderedQueue:
                print(req.__str__() + " , ")

    def printInboundACKS(self):
        if not len(self.inboundACKs) == 0:
            print("Node " + str(self.nodeID) + " InboundACK -> ")
            for req in self.inboundACKs:
                print(req + " , ")
    
    def printInboundREQS(self):
        if not len(self.inboundREQs) == 0:
            print("Node " + str(self.nodeID) + " InboundREQ -> ")
            for req in self.inboundREQs:
                print(req.__str__() + " , ")
    
    def printDeliveredMSG(self):
        if not len(self.deliveredMSGs) == 0:
            print("Node " + str(self.nodeID) + " Delivered Msg -> ")
            for req in self.deliveredMSGs:
                print(req.__str__() + ", ")

