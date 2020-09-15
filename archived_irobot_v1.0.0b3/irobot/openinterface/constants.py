__author__ = 'Matthew Witherwax (lemoneer)'


class Constant(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


BAUD_RATE           = Constant(BAUD_300=0, BAUD_600=1, BAUD_1200=2, BAUD_2400=3, BAUD_4800=4, BAUD_9600=5, BAUD_14400=6,
                               BAUD_19200=7, BAUD_28800=8, BAUD_38400=9, BAUD_57600=10, BAUD_115200=11, DEFAULT=11)
DAYS                = Constant(SUNDAY=0x01, MONDAY=0x02, TUESDAY=0x04, WEDNESDAY=0x08, THURSDAY=0x10, FRIDAY=0x20,
                               SATURDAY=0x40)
DRIVE               = Constant(STRAIGHT=0x8000, STRAIGHT_ALT=0x7FFF, TURN_IN_PLACE_CW=0xFFFF, TURN_IN_PLACE_CCW=0x0001)
MOTORS              = Constant(SIDE_BRUSH=0x01, VACUUM=0x02, MAIN_BRUSH=0x04, SIDE_BRUSH_DIRECTION=0x08,
                               MAIN_BRUSH_DIRECTION=0x10)
LEDS                = Constant(DEBRIS=0x01, SPOT=0x02, DOCK=0x04, CHECK_ROBOT=0x08)
WEEKDAY_LEDS        = Constant(SUNDAY=0x01, MONDAY=0x02, TUESDAY=0x04, WEDNESDAY=0x08, THURSDAY=0x10, FRIDAY=0x20,
                               SATURDAY=0x40)
SCHEDULING_LEDS     = Constant(COLON=0x01, PM=0x02, AM=0x04, CLOCK=0x08, SCHEDULE=0x10)
RAW_LED             = Constant(A=0x01, B=0x02, C=0x04, D=0x08, E=0x10, F=0x20, G=0x40)
BUTTONS             = Constant(CLEAN=0x01, SPOT=0x02, DOCK=0x04, MINUTE=0x08, HOUR=0x10, DAY=0x20, SCHEDULE=0x40,
                               CLOCK=0x80)
ROBOT               = Constant(TICK_PER_REV=508.8, WHEEL_DIAMETER=72, WHEEL_BASE=235,
                               TICK_TO_DISTANCE=0.44456499814949904317867595046408)
MODES               = Constant(OFF=0, PASSIVE=1, SAFE=2, FULL=3)
WHEEL_OVERCURRENT   = Constant(SIDE_BRUSH=0x01, MAIN_BRUSH=0x02, RIGHT_WHEEL=0x04, LEFT_WHEEL=0x08)
BUMPS_WHEEL_DROPS   = Constant(BUMP_RIGHT=0x01, BUMP_LEFT=0x02, WHEEL_DROP_RIGHT=0x04, WHEEL_DROP_LEFT=0x08)
CHARGE_SOURCE       = Constant(INTERNAL=0x01, HOME_BASE=0x02)
LIGHT_BUMPER        = Constant(LEFT=0x01, FRONT_LEFT=0x02, CENTER_LEFT=0x04, CENTER_RIGHT=0x08, FRONT_RIGHT=0x10,
                               RIGHT=0x20)
STASIS              = Constant(TOGGLING=0x01, DISABLED=0x02)

POWER_SAVE_TIME = 300   # seconds

RESPONSE_SIZES = {0: 26, 1: 10, 2: 6, 3: 10, 4: 14, 5: 12, 6: 52,
                  # actual sensors
                  7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 2, 20: 2, 21: 1,
                  22: 2, 23: 2, 24: 1, 25: 2, 26: 2, 27: 2, 28: 2, 29: 2, 30: 2, 31: 2, 32: 3, 33: 3, 34: 1, 35: 1,
                  36: 1, 37: 1, 38: 1, 39: 2, 40: 2, 41: 2, 42: 2, 43: 2, 44: 2, 45: 1, 46: 2, 47: 2, 48: 2, 49: 2,
                  50: 2, 51: 2, 52: 1, 53: 1, 54: 2, 55: 2, 56: 2, 57: 2, 58: 1,
                  # end actual sensors
                  100: 80, 101: 28, 106: 12, 107: 9}
