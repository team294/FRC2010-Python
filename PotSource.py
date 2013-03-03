from wpilib import PIDSource

class PotSource(PIDSource):
    def __init__(self, pot):
        PIDSource.__init__(self)
        self.pot = pot

    def Get(self):
        return self.pot.GetAverageValue()
    
    def PIDGet(self):
        return self.Get()

