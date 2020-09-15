from __future__ import print_function
__author__ = 'Matthew Witherwax (lemoneer)'

import logging
from sys import stdout
from re import match
from six.moves import input
from irobot.robots.create2 import Create2, RobotConnectionError, ModeChangeError
from irobot.openinterface.constants import MODES, RAW_LED

FIRMWARE_PREFIX = '^r3[_-]robot\/tags\/release-'
FIRMWARE_PREFIX_LENGTH = 22


def check_for_quirks(robot):

    print('Checking firmware for quirks')
    print('Restarting Robot...')

    boot_message = robot.firmware_version.split(u'\r\n')
    for line in boot_message:
        if match(FIRMWARE_PREFIX, line):
            print('Found firmware:', line)
            line = line[FIRMWARE_PREFIX_LENGTH:]
            if ':' in line:
                line = line.split(':')[0]
            major, minor, point = line.split('.')
            if int(major) < 3 or (int(major) == 3 and int(minor) < 3):
                print('Enabling quirks')
                robot.enable_quirks = True
            else:
                print('No known quirks')
                robot.enable_quirks = False
            print()
            return

    print('Could not determine firmware')
    print('Enabling quirks for safety')
    robot.enable_quirks = True


def _configure_logger():
    class Formatter(logging.Formatter):
        def __init__(self, fmt):
            logging.Formatter.__init__(self, fmt)

        def format(self, record):
            msg = logging.Formatter.format(self, record)
            lines = msg.split('\n')
            return '{0}\n{1}'.format(
                lines[0],
                '\n'.join(['\t{0}'.format(line) for line in lines[1:]]))

    logger = logging.getLogger('Create2')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(Formatter('%(levelname)s\n%(message)s'))
    logger.addHandler(ch)
    logger.disabled = True

    return logger


def main():
    import code

    print('Launching REPL')
    port = input('Serial Port> ')
    print()

    # give the user a way out before we launch into interactive mode
    if port.lower() == 'quit()':
        return
    try:
        robot = Create2(port)
    except RobotConnectionError as e:
        print(e, '\nInner Exception:', e.__cause__)
        return
    except ModeChangeError:
        print('Failed to enter Passive mode')
        return

    # add methods to turn logging to console on/off
    logger = _configure_logger()

    def enable_logging():
        logger.disabled = False

    def disable_logging():
        logger.disabled = True

    # determine if we need to handle the issue with angle/distance
    check_for_quirks(robot)

    # add our goodies to the scope
    # I hope the Python powers don't come to get me foe doing this
    vars = globals().copy()
    vars.update(locals())
    # punch user out to a repl
    shell = code.InteractiveConsole(vars)
    shell.interact(banner='Create2 attached as robot on {0}\nMay it serve you well'.format(port))

if __name__ == "__main__":
    main()
