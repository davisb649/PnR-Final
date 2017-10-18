import pigo
import time  # import just in case students need
import random

# setup logs
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/PnR-Final/log_robot.log"  # don't forget to make this file!
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


class Piggy(pigo.Pigo):
    """Student project, inherits teacher Pigo class which wraps all RPi specific functions"""

    def __init__(self):
        """The robot's constructor: sets variables and runs menu loop"""
        print("I have been instantiated!")
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 109
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 30
        self.HARD_STOP_DIST = 15
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.LEFT_SPEED = 130
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 130
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        # let's use an event-driven model, make a handler of sorts to listen for "events"
        while True:
            self.stop()
            self.menu()

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values
        # You may change the menu if you'd like to add an experimental method
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "c": ("Calibrate", self.calibrate),
                "s": ("Check status", self.status),
                "q": ("Quit", quit_now),
                "o": ("Obstacle count", self.detect_obst)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = raw_input("Your selection: ")
        # activate the item selected
        menu.get(ans, [None, error])[1]()

    # YOU DECIDE: How does your GoPiggy dance?
    def dance(self):
        """executes a series of methods that add up to a compound dance"""
        print("\n---- LET'S DANCE ----\n")
        ##### WRITE YOUR FIRST PROJECT HERE
        if self.safety_check():
            self.to_the_right()
            self.to_the_left()
            self.spin_time()
            self.cha_cha()
            self.walk_it_by_yourself()

    def safety_check(self):
        self.servo(self.MIDPOINT)  # look forward
        # loop 3 more times
        for x in range(5):
            if x == 0:
                self.encR(2)
            if not self.is_clear():
                print("It's not safe to dance")
                return False
            if x == 4:
                print("I've got enough dancing space")
                self.encR(1)
            else:
                self.encR(6)
        return True


    def to_the_right(self):
        """Circle on the right"""
        for x in range(4):
            self.servo(133)
            self.encR(10)
            self.encF(5)
            self.encR(10)
            self.encB(5)
            self.servo(103)

    def to_the_left(self):
        """Circle on the left"""
        for x in range(4):
            self.servo(73)
            self.encL(10)
            self.encB(5)
            self.encL(10)
            self.encF(5)
            self.servo(103)

    def spin_time(self):
        """Pivot w/ servo"""
        for x in range(4):
            if x % 2 == 0:
                self.servo(133)
                self.encL(6)
            else:
                self.servo(73)
                self.encR(6)
            self.servo(103)

    def shake_it(self):
        """Let's shake"""
        for x in range(2):
            self.encF(4)
            for y in range(2):
                self.encL(2)
                self.encR(2)

    def cha_cha(self):
        """Chacha real smooth"""
        for x in range(4):
            for y in range(2):
                self.servo(133)
                self.servo(73)
                self.servo(133)
                self.servo(73)
            if x % 2 == 0:
                self.encF(18)
            else:
                self.encB(18)
            self.servo(103)

    def cruise(self):
        """Go straight while the path is clear"""
        self.fwd()
        self.servo(self.MIDPOINT)
        while self.dist() > self.SAFE_STOP_DIST:
            time.sleep(.5)
        self.stop()

    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        while True:
            """if you can, go"""
            if self.is_clear():
                self.cruise()
            else:
                """decide"""
                while not self.is_clear():
                    """check on your right"""
                    self.right_rot()
                rdist = self.dist()
                self.encR(1)
                while not self.is_clear():
                    """check on your left"""
                    self.left_rot()
                ldist = self.dist()
                if rdist > ldist:
                    """which is farther?"""
                    while not self.is_clear():
                        self.right_rot()
                    self.fwd()
                else:
                    self.fwd()
# How many obstacles
    def detect_obst(self):
        """Finding them obstacles"""
        obst_found = 0
        prev_dist = 150
        maxdist = 350
        self.wide_scan()
        for dist in self.scan:
            print("Hi")
            if dist and int(dist) < maxdist:
                if int(prev_dist - int(dist)) > 50:
                    print("I found obstacle # %d" % obst_found)
                    obst_found += 1
                if int(prev_dist - int(dist)) > 50:
                    print("I don't see the obstacle anymore")
            prev_dist = dist
        print("\n-----I found a total of %d obstacles.-----\n" % obst_found)




####################################################
############### STATIC FUNCTIONS

def error():
    """records general, less specific error"""
    logging.error("ERROR")
    print('ERROR')


def quit_now():
    """shuts down app"""
    raise SystemExit

##################################################################
######## The app starts right here when we instantiate our GoPiggy


try:
    g = Piggy()
except (KeyboardInterrupt, SystemExit):
    pigo.stop_now()
except Exception as ee:
    logging.error(ee.__str__())
