from RobotLEDTracks import RobotLEDSolid

numLEDs = 144
maxBrightness = 4
order = 'rgb'

invalidColor  = 0x800080    # purple

ledMode = RobotLEDSolid(numLEDs, maxBrightness, order, invalidColor)

