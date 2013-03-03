from wpilib import PIDOutput
from Globals import *

class WinchOutput(PIDOutput):
    def __init__(self, winchMotor, pot):
        PIDOutput.__init__(self)
        self.winchMotor = winchMotor
        self.pot = pot

    def Set(self, speed):
        potval = self.pot.Get()
        if (speed < 0 and potval < gWinchFull) or (speed > 0 and potval > gWinchOut):
            self.winchMotor.Set(0.0)
        else:
            self.winchMotor.Set(speed)

    def PIDWrite(self, output):
        self.Set(output)

