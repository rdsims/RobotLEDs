from RobotLEDTracks import RobotLEDSolid, RobotLEDPulse, RobotLEDTracks
from enum import IntEnum
from networktables import NetworkTable
import time



numLEDs = 144
fps = 50.0
dt = 1.0 / fps
maxSpeed = 100.0

maxBrightness = 4
order = 'rgb'

invalidColor  = 0x800080    # purple
disabledColor = 0x00FF00    # green
fwdColor      = 0x0000FF    # blue
revColor      = 0xFF0000    # red

treadWidth   = 10
treadSpacing = 10
ledStripPixelSpacing = 0.275

NetworkTable.setIPAddress('roboRIO-9686-FRC.local')
NetworkTable.setClientMode()
NetworkTable.initialize()
sd = NetworkTable.getTable('SmartDashboard')

class OpMode(IntEnum):
    INVALID = -1
    DISABLED = 0
    AUTONOMOUS = 1
    TELEOP = 2
    TEST = 3

prevOpMode = OpMode.INVALID    # set to an invalid value so we can tell when we connect to SmartDashboard

print('Starting robotLEDs.py')

ledMode = RobotLEDSolid(numLEDs, maxBrightness, order, invalidColor)

while True:  # Loop forever

    try:
        opMode = OpMode(sd.getNumber('OperationalMode'))

        # detect opMode change
        if (opMode != OpMode.INVALID) and (prevOpMode == OpMode.INVALID):
            print('Connected to SmartDashboard')
            ledMode.cleanup
            ledMode = RobotLEDPulse(numLEDs, 31, order, disabledColor, 2.0/dt)

        if (opMode > OpMode.DISABLED) and (prevOpMode == OpMode.DISABLED):
            print('Robot Enabled')
            ledMode.cleanup
            ledMode = RobotLEDTracks(numLEDs, maxBrightness, order, fwdColor, revColor,
                                     treadWidth, treadSpacing, ledStripPixelSpacing,
                                     dt, maxSpeed)

        elif (opMode == OpMode.DISABLED) and (prevOpMode > OpMode.DISABLED):
            print('Robot Disabled')
            ledMode.cleanup
            ledMode = RobotLEDPulse(numLEDs, maxBrightness, order, disabledColor, 2.0/dt)

        prevOpMode = opMode

        # run
        if (opMode > OpMode.DISABLED):
            try:
                lSpeed = sd.getNumber('lVelocity')
                rSpeed = sd.getNumber('rVelocity')
                ledMode.setSpeed(lSpeed, rSpeed)

            except KeyError:
                print('Error: "lVelocity", "rVelocity" not found in SmartDashboard')

    except KeyError:
        print('Error: "OperationalMode" not found in SmartDashboard')

    updated = ledMode.update()
    time.sleep(dt)

