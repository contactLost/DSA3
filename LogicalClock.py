class LogicalClock:
    def __init__(self):
        self.clock: int = 0

    def increaseClock(self):
        self.clock = self.clock + 1
        return self.clock

    def updateClock(self,newClock):
        if newClock > self.clock:
            self.clock = newClock + 1
        else:
            self.clock = self.clock + 1

        return self.clock

    def getClock(self):
        return self.clock