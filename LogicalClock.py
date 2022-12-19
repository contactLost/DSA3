class LogicalClock:
    def __init__(self):
        self.clock: int = 0

    def increaseClock(self):
        self.clock = self.clock + 1
        return self.clock

    def updateClock(self,newClock):
        self.clock = newClock
        return self.clock

    def getClock(self):
        return self.clock