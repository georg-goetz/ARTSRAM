__author__ = 'Matthew Witherwax (lemoneer)'

import unittest

from irobot.openinterface.commands import *


def to_str(data):
    return '[' + '|'.join((('0x%0.2X' % b) for b in data)) + ']'


class TestCommands(unittest.TestCase):
    def test_drive(self):
        cmd = drive(-200, 500)
        self.assertEqual(to_str(cmd), '[0x89|0xFF|0x38|0x01|0xF4]')

    def test_get_days(self):
        cmd = get_days(sun_hour=0, sun_min=0, mon_hour=0, mon_min=0, tues_hour=0, tues_min=0, wed_hour=15, wed_min=0,
                       thurs_hour=0, thurs_min=0, fri_hour=10, fri_min=36, sat_hour=0, sat_min=0)
        self.assertEquals(40, cmd)

    def test_set_schedule(self):
        cmd = set_schedule(sun_hour=0, sun_min=0, mon_hour=0, mon_min=0, tues_hour=0, tues_min=0, wed_hour=15,
                           wed_min=0, thurs_hour=0, thurs_min=0, fri_hour=10, fri_min=36, sat_hour=0, sat_min=0)
        self.assertEqual(to_str(cmd),
                         '[0xA7|0x28|0x00|0x00|0x00|0x00|0x00|0x00|0x0F|0x00|0x00|0x00|0x0A|0x24|0x00|0x00]')

    def test_set_motors(self):
        cmd = set_motors(True, False, True, True, False)
        self.assertEqual(to_str(cmd), '[0x8A|0x0D]')

    def test_set_leds(self):
        cmd = set_leds(False, False, True, False, 0, 128)
        self.assertEqual(to_str(cmd), '[0x8B|0x04|0x00|0x80]')

    def test_set_ascii_leds(self):
        cmd = set_ascii_leds(65, 66, 67, 68)
        self.assertEqual(to_str(cmd), '[0xA4|0x41|0x42|0x43|0x44]')

    def test_set_song(self):
        cmd = set_song(0, [(31, 32), (85, 100)])
        self.assertEqual(to_str(cmd), '[0x8C|0x00|0x02|0x1F|0x20|0x55|0x64]')
