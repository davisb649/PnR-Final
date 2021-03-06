import pigo
import time  # import just in case students need
import random
import datetime

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
        self.start_time = datetime.datetime.utcnow()
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 109
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 35
        self.HARD_STOP_DIST = 5
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.LEFT_SPEED = 127
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 130
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        self.clear = False
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
                "o": ("Obstacle count", self.detect_obst),
                "p": ("Safest Path", self.safest_path),
                "r": ("Rotation Testing", self.rotation_testing),
                "h": ("Restore Heading", self.restore_heading),
                "t": ("Test Restore Heading", self.rh_test),
                "e": ("Encoder Testing", self.enc_tester)
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
            #self.walk_it_by_yourself()

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
        if self.dist() < self.SAFE_STOP_DIST:
            time.sleep(.1)

    def space_checking(self):
        """check to the left and to the right and figure out which way to go that's closest to the original direction"""
        self.encB(4)
        orig_tt = self.turn_track
        while self.dist() < (self.SAFE_STOP_DIST + 5):
            self.encR(2)
            time.sleep(.1)
        right_tt = self.turn_track - orig_tt
        self.encL(right_tt)
        while self.dist() < (self.SAFE_STOP_DIST + 5):
            self.encL(2)
            time.sleep(.1)
        left_tt = self.turn_track - orig_tt
        self.encR(abs(left_tt))
        if abs(right_tt + orig_tt) > abs(left_tt + orig_tt):
            self.encL(abs(left_tt) + 1)
        else:
            self.encR(abs(right_tt + 1))
        self.clear = self.servo_search_nav()
        if not self.clear:
            self.restore_heading()
        self.clear = False



    def servo_search_nav(self):
        self.servo(self.MIDPOINT - 2)
        if self.dist() > self.SAFE_STOP_DIST:
            self.servo(self.MIDPOINT + 2)
            if self.dist() > self.SAFE_STOP_DIST:
                self.servo(self.MIDPOINT)
                return True
        self.servo(self.MIDPOINT)
        return False




    def enc_tester(self):
        print(self.dist())
        self.encF(1)
        print(self.dist())

    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        right_now = datetime.datetime.utcnow()
        difference = (right_now - self.start_time).seconds
        print("It took you %d seconds to run this" % difference)
        while True:
            if self.dist() > self.SAFE_STOP_DIST:
                self.cruise()
            else:
                self.space_checking()

    def smooth_turn(self):
        time_start = datetime.datetime.utcnow()
        self.servo(self.MIDPOINT)
        self.right_rot()
        while True > 100:
            if self.dist():
                self.stop()
                print("I think I found a safe place to go")
            elif datetime.datetime.utcnow() - time_start > datetime.timedelta(seconds=10):
                self.stop()
                print("I give up.")
            time.sleep(.2)

    def detect_obst(self):
        """Turning 360 degrees and looking for all of the obstacles around it"""
        obst_found = 0
        maxdist = 90
        prev_dist = 150
        for x in range(3):
            self.wide_scan()
            for dist in self.scan:
                if dist:
                    if int(prev_dist - int(dist)) > 50:
                        if prev_dist < maxdist or int(dist) < maxdist:
                            obst_found += 1
                            print("I found obstacle # %d" % obst_found)
                    if int(prev_dist - int(dist)) < -50:
                        if prev_dist < maxdist or int(dist) < maxdist:
                            print("I don't see the obstacle anymore")
                    prev_dist = dist
            self.encR(11)
        print("\n-----I found a total of %d obstacles.-----\n" % obst_found)

    def safest_path(self):
        """find the safest way to travel; safest is the way with most space btwn obstacles"""
        """create all lists and set variables to be overwritten"""
        angle_go = []
        width = []
        free_space = 0
        largest_angle = 0
        init_space = 360
        """scan it 18 encoders"""
        for x in range(3):
            """take the distances first"""
            self.wide_scan()
            for angle, dist in enumerate(self.scan):
                if dist:
                    """if it's a free space"""
                    if int(dist) > 90:
                        """and it's the start of said space"""
                        if free_space == 0:
                            """declare where the space starts"""
                            init_space = angle
                        """add width of space"""
                        free_space += 1
                    """but if it is an object, not a free space"""
                    if int(dist) < 91:
                        """the space has ended and put a width and angle measurement into the list"""
                        free_space = 0
                        width.append(angle-init_space)
                        angle_go.append((angle+init_space)/2-60)
            """turn to scan more space"""
            self.encL(9)
        """test each of the angle measurements for width to see which is the largest"""
        for number, ang in enumerate(width):
            """if there's a newly discovered largest angle"""
            if ang > largest_angle:
                """set a the largest angle to be that newly found one"""
                largest_angle = ang
        """and then go once all of them are tested and a definitive largest is named"""
        self.servo(109)
        self.encL(int(angle_go[largest_angle] / 12))

    def rotation_testing(self):
        """Just testing how strong the motors are by rotating until i hit 360 deg"""
        self.encL(30)
        self.restore_heading()

    def restore_heading(self):
        """turns back the way i'm supposed to be going by using self.turn_track()"""
        print("Restoring heading!")
        if self.turn_track > 0:
            self.encL(abs(self.turn_track))
        elif self.turn_track < 0:
            self.encR(abs(self.turn_track))

    def rh_test(self):
        self.encR(10)
        self.encL(1)
        self.encR(8)
        self.encL(3)
        self.encR(6)
        self.encL(5)
        self.encR(4)
        self.encL(7)
        self.encR(2)
        self.encL(9)

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
