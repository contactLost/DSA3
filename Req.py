import constants

class Req:
    def __init__(self, sender, time, reqNo, reqString):
        self.sender = sender
        self.time = time
        self.reqNo = reqNo
        self.reqString = reqString
        self.ackCounter = 0

    def ackRequest(self, ackMsg):
        if ackMsg[4:] == self.reqString[4:]:
            self.ackCounter = self.ackCounter + 1
            return True
        return False

    def is_request_acked_by_everyone(self):
        if constants.NP - 1 == self.ackCounter:
            return True
        return False
