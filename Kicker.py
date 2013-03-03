import wpilib
from Config import *
from Globals import *

__all__ = ["Kicker"]

def getNotchPosition(notch):
    return gWinchNotchOne + (notch - 1) * gWinchPerNotch

class Kicker:
    def __init__(self):
        self.armed = False
        self.retraction = getNotchPosition(10)
        self.winchTarget = getNotchPosition(10)
        self.kickTime = wpilib.Timer()
        self.pneumaticTime = wpilib.Timer()

        self.kickTime.Start()
        self.pneumaticTime.Start()

        self.raw10Previous = False
        self.raw11Previous = False

        self.i = 0

    def RunWinch(self):
        """Winch control of kicker (used in both auto and teleop).
        Returns True when winch target reached."""
        if self.IsWinchOnTarget():
            winchControl.Disable()
            return True
        # Use PID control
        winchControl.Enable()
        winchControl.SetSetpoint(self.winchTarget)
        if self.armed:
            #winchControl.SetPID(1.0/50.0, 0.0, 1.0/50.0)
            winchControl.SetPID(1.0/50.0, 0.0, 1.0/50.0)
        else:
            #winchControl.SetPID(1.0/30.0, 0.0, 0.0)
            winchControl.SetPID(1.0/18.0, 0.0, 1.0/40.0)
        return self.IsWinchOnTarget()

    def IsWinchOnTarget(self):
        potval = winchPot.Get()
        if potval <= gWinchNotchOne and self.winchTarget <= gWinchNotchOne:
            return True
        error = potval - self.winchTarget
        if error < -gWinchDeadband:
            return False
        elif error > gWinchDeadband:
            return False
        else:
            return True

    def IsKickComplete(self):
        return self.kickTime.Get() > gWinchWaitTime

    def Arm(self):
        ratchet1.Set(True)
        ratchet2.Set(False)
        self.armed = True
        self.pneumaticTime.Reset()
        print("ARMED!!")

    def Fire(self):
        intakeMotor.Set(0.0)
        ratchet1.Set(False)
        ratchet2.Set(True)
        self.armed = False
        self.pneumaticTime.Reset()
        self.kickTime.Reset()
        print("KICKED!!")

    def ClearRatchetPneumatics(self):
        ratchet1.Set(False)
        ratchet2.Set(False)

    def AutoArm(self, notch, do_arm=True):
        """Autonomous-only arming of kicker.
        Returns True when kicker is ready to fire."""
        if not self.armed:
            # winch back
            self.winchTarget = getNotchPosition(notch)
            if self.RunWinch() and do_arm:
                self.Arm()      # arm when we're done winching back
        else:
            # we're armed, so unwinch
            self.winchTarget = gWinchOut
            if self.RunWinch() and self.kickTime.Get() > gBetweenKickTime:
                return True     # armed and ready to fire!
        return False

    def AutoPeriodic(self):
        # Reset pneumatics
        if self.pneumaticTime.Get() > 0.3:
            self.ClearRatchetPneumatics()

    def OperatorControl(self):
        # Reset pneumatics
        if self.pneumaticTime.Get() > 0.3:
            self.ClearRatchetPneumatics()

        # Set kicker strength
        if stick3.GetRawButton(3):
            self.retraction = getNotchPosition(7)
        elif stick3.GetRawButton(5):
            self.retraction = getNotchPosition(2)
        elif stick3.GetRawButton(4):
            self.retraction = getNotchPosition(10)

        # Kicker debug code
        if stick3.GetRawButton(10) and not self.raw10Previous:
            self.retraction -= gWinchPerNotch
        elif stick3.GetRawButton(11) and not self.raw11Previous:
            self.retraction += gWinchPerNotch
        self.raw10Previous = stick3.GetRawButton(10)
        self.raw11Previous = stick3.GetRawButton(11)

        if self.retraction < getNotchPosition(1):
            self.retraction = getNotchPosition(1)
        elif self.retraction > getNotchPosition(22):
            self.retraction = getNotchPosition(22)

        # Kicker arm and fire control
        if not self.armed:
            # wait after kick before starting to winch back
            if self.IsKickComplete():
                self.winchTarget = self.retraction
                if self.IsWinchOnTarget():
                    # auto arming mode
                    autoArm = False  #not dseio.GetDigital(15)

                    # arm; this starts the unwinch
                    if (stick3.GetTop() and not autoArm) or autoArm:
                        self.Arm()
        else: # armed
            # unwinch
            self.winchTarget = gWinchOut
            if winchPot.Get() < (self.winchTarget + gWinchDeadband):
                pass#dseio.SetDigitalOutput(3, 1)
            # fire!
            if (self.kickTime.Get() > gBetweenKickTime
                and winchPot.Get() < (self.winchTarget + gWinchDeadband)
                and stick3.GetTrigger()):
                self.Fire()

        # manual control override on winch
        if stick3.GetRawButton(9):
            winchControl.Disable()
            kickerMotor.Set(stick3.GetY())
            self.armed = False
            self.retraction = getNotchPosition(10)
        else:
            # automatic winch control
            if self.i%5 == 0:
                print("S: %i, T: %i" % (winchPot.Get(), self.winchTarget))
                #print("BL: %i  TL: %i" % (self.winchTarget-gWinchDeadband,
                #                          self.winchTarget+gWinchDeadband))
                #print("")
            self.i += 1
            self.RunWinch()

        # Manual override on kicker pneumatic
        if rstick.GetTop():
            ratchet1.Set(True)
            ratchet2.Set(False)
            self.pneumaticTime.Reset()
        elif lstick.GetTop():
            ratchet1.Set(False)
            ratchet2.Set(True)
            self.pneumaticTime.Reset()

