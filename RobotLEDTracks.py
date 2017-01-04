from RobotLEDTemplate import RobotLEDTemplate


class RobotLEDSolid(RobotLEDTemplate):

    def __init__(self, numLEDs, globalBrightness, order, color=0xFF0000):
        super(RobotLEDSolid, self).__init__(numLEDs, globalBrightness, order)
        self.color = color
        self.init()

    def init(self):
        for led in range(0, self.numLEDs):
            self.strip.setPixelRGB(led, self.color)     # Paint all LEDs with same color
        self.strip.show()

    def update(self):
        # Do nothing: Init lit the strip, and update just keeps it this way
        return 0




class RobotLEDPulse(RobotLEDTemplate):

    def __init__(self, numLEDs, maxGlobalBrightness, order, color=0xFF0000, period=100):
        self.maxGlobalBrightness = maxGlobalBrightness
        super(RobotLEDPulse, self).__init__(numLEDs, 0, order)
        self.color = color
        self.qtrPeriod = period / 4.0
        self.t = 0
        self.mBrightness = self.strip.getGlobalBrightness()
        self.deltaBrightness = self.maxGlobalBrightness / self.qtrPeriod
        self.state = 0
        self.init()

    def init(self):
        for led in range(0, self.numLEDs):
            self.strip.setPixelRGB(led, self.color)     # Paint all LEDs with same color
        self.strip.show()

    def update(self):
        self.t += 1
        if self.t > self.qtrPeriod:
            self.t -= self.qtrPeriod
            self.state += 1
            if self.state >= 4:
                self.state = 0

        if self.state == 0:
            self.mBrightness += self.deltaBrightness
        elif self.state == 1:
            self.mBrightness -= self.deltaBrightness
        else:
            self.mBrightness = self.mBrightness  # stay at 0 for full period

        self.mBrightness = max(self.mBrightness, 0)
        self.mBrightness = min(self.mBrightness, self.maxGlobalBrightness)

        newBrightness = int(self.mBrightness)
        oldBrightness = self.strip.getGlobalBrightness()
        if newBrightness != oldBrightness:
            self.strip.setGlobalBrightness(newBrightness)
            self.strip.show()





class Track:
    trackLen = 0
    pixelSpacing = 0.0
    speed = 0.0
    maxSpeed = 100.0
    dt = 0.0
    dist = 0.0
    head = 0
    prevValue = 0
    writeOffset = 0
    writeDir = +1
    fwdColor = 0
    revColor = 0


class RobotLEDTracks(RobotLEDTemplate):

    def __init__(self, numLEDs, globalBrightness, order, fwdColor=0x0000FF, revColor=0xFF0000,
                 treadWidth=10, treadSpacing=10, pixelSpacing=0.25, dt=0.01, maxSpeed = 100.0):
        super(RobotLEDTracks, self).__init__(numLEDs, globalBrightness, order)

        self.treadTemplate = [0] * (treadWidth+treadSpacing)
        for k in range(0,treadWidth):
            self.treadTemplate[k] = 0xFFFFFF    # set to white here, will mask with fwd/rev color below
        for k in range(treadWidth+1, treadWidth+treadSpacing):
            self.treadTemplate[k] = 0

        self.lTrack = Track()
        self.rTrack = Track()

        self.lTrack.trackLen = int(numLEDs/2)
        self.rTrack.trackLen = int(numLEDs/2)

        self.lTrack.pixelSpacing = pixelSpacing
        self.rTrack.pixelSpacing = pixelSpacing

        self.lTrack.maxSpeed = maxSpeed
        self.rTrack.maxSpeed = maxSpeed

        self.lTrack.dt = dt
        self.rTrack.dt = dt

        self.lTrack.fwdColor = fwdColor
        self.rTrack.fwdColor = fwdColor

        self.lTrack.revColor = revColor
        self.rTrack.revColor = revColor

        # here's where the differences between the left and right tracks lie
        self.lTrack.writeOffset =  numLEDs-1
        self.lTrack.writeDir    = -1

        self.rTrack.writeOffset =  0
        self.rTrack.writeDir    = +1

        self.init()


    def init(self):
        # draw the left and right tracks
        self.lTrack.prevValue = -1
        self.rTrack.prevValue = -1
        self.update()


    def draw_tread(self, track):

        retVal = 0
        track.dist += track.speed * track.dt

        while track.dist >= track.pixelSpacing:
            track.dist -= track.pixelSpacing
            track.head += 1
            if track.head >= len(self.treadTemplate):
                track.head = 0

        while track.dist < 0:
            track.dist += track.pixelSpacing
            track.head -= 1
            if track.head < 0:
                track.head = len(self.treadTemplate)-1

        if track.head != track.prevValue:
            retVal = 1
            track.prevValue = track.head

            if track.speed >= 0.0:
                color = track.fwdColor
            else:
                color = track.revColor

            p = track.head
            for k in range(0, track.trackLen):
                s = track.writeOffset + track.writeDir*k
                self.strip.setPixelRGB(s, self.treadTemplate[p] & color)
                p += 1
                if p >= len(self.treadTemplate):
                    p = 0

        return retVal



    def draw_bar(self, track):

        retVal = 0
        power = abs(track.speed) / track.maxSpeed / 2
        mid = int(track.trackLen/2)

        d = int(power * track.trackLen)
        if d != track.prevValue:
            retVal = 1
            track.prevValue = d
            
            start = 0
            end   = min(d, mid)

            if track.speed >= 0.0:
                color = track.fwdColor
            else:
                color = track.revColor

            for k in range(0, mid):
                s1 = track.writeOffset + track.writeDir*(mid+k)
                s2 = track.writeOffset + track.writeDir*(mid-k)
                if k>=end:
                    color = 0
                self.strip.setPixelRGB(s1, color)
                self.strip.setPixelRGB(s2, color)

    

        return retVal



    def setSpeed(self, lSpeed, rSpeed):
        self.lTrack.speed = lSpeed
        self.rTrack.speed = rSpeed


    def update(self):

        lUpdate = self.draw_tread(self.lTrack)
        rUpdate = self.draw_tread(self.rTrack)
#        lUpdate = self.draw_bar(self.lTrack)
#        rUpdate = self.draw_bar(self.rTrack)

        if lUpdate or rUpdate:
            self.strip.show()







