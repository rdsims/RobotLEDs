import apa102

"""
This class is the basis of all robot LED subclasses.
A specific LED scheme must subclass this template, and implement at least the
'update' method.
"""


class RobotLEDTemplate:
    def __init__(self, numLEDs, globalBrightness=4, order='bgr'):     # Init method
        self.numLEDs = numLEDs                      # The number of LEDs in the strip
        self.globalBrightness = globalBrightness    # Brightness of the strip
        self.order = order                          # Strip color ordering
        self.initialized = False
        self.strip = apa102.APA102(numLEDs=self.numLEDs, globalBrightness=self.globalBrightness,
                                   order=self.order)  # Initialize the strip

    """
    void init()
    This method is called to initialize a color program.
    """
    def init(self):
        # The default does nothing. A particular subclass could setup variables, or
        # even light the strip in an initial color.
        pass

    """
    void shutdown()
    This method is called at the end, when the light program should terminate
    """
    def shutdown(self):
        # The default does nothing
        pass

    """
    void update()
    This method paints one subcycle. It must be implemented
    """
    def update(self):
        raise NotImplementedError("Please implement the update() method")

    def cleanup(self):
        self.shutdown()
        self.strip.clearStrip()
        self.strip.cleanup()
        self.initialized = False

    """
    Start the actual work
    """
    def start(self):
        try:
            if not self.initialized:
                self.strip.clearStrip()
                self.init()                 # Call the subclasses init method
                self.strip.show()
                self.initialized = True

            needRepaint = self.update()     # Call the subclasses update method
            if needRepaint:
                self.strip.show()           # Display, only if required

        except KeyboardInterrupt:           # Ctrl-C can halt the light program
            print('Interrupted...')
            self.cleanup()
