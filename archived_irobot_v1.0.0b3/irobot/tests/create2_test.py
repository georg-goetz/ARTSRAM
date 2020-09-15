__author__ = 'Matthew Witherwax (lemoneer)'

from time import sleep
from six.moves import input
from irobot.robots.create2 import Create2


def print_properties(obj, level=1):
    if not hasattr(obj, '__dict__'):
        print('\t' * level, obj)
    else:
        for prop in [prop for prop in dir(obj) if not prop.startswith('_')]:
            prop_val = getattr(obj, prop)
            if not hasattr(prop_val, '__dict__'):
                print('\t' * level, prop + ':', prop_val)
            else:
                print('\t' * level, prop + ':')
                print_properties(prop_val, level + 1)


def get_all_sensor_readings(robot):
    print('Reading all sensors')
    for p in [p for p in dir(Create2) if
              isinstance(getattr(Create2, p), property) and p not in ['enable_quirks', 'enable_logging',
                                                                      'firmware_version']]:
        print(p)
        print_properties(getattr(robot, p))
        print()
        sleep(.03)


if __name__ == "__main__":
    print('Launching robots Tests')
    port = input('Serial Port?> ')
    robot = Create2(port, enable_quirks=True)
    get_all_sensor_readings(robot)
    robot.stop()
