import constants

class Req:
    def __init__(self, sender, time, reqNo, reqString):
        self.sender = sender
        self.time = time
        self.reqNo = reqNo
        self.reqString = reqString
        self.ackCounter = 0

    def ackRequest(self, ackMsg):
        ack = ackMsg.split(",")
        ackStr = ack[3] + "," + ack[4] + "," + ack[5]
        if ackStr == self.get_request_data():
            self.ackCounter = self.ackCounter + 1
            return True
        return False

    def is_request_acked_by_everyone(self):
        if constants.NP - 1 == self.ackCounter:
            return True
        return False

    def get_request_data(self):
        return self.reqString[4:]

    def __str__(self):
        return "Sender: " + self.sender + ", Time: " + str(self.time) + ", ReqNo: " + str(self.reqNo) + ", ReqStr: " + self.reqString + ", AckCounter: " + str(self.ackCounter)
