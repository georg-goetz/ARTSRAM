__author__ = 'Matthew Witherwax (lemoneer)'

from struct import Struct

from .constants import WHEEL_OVERCURRENT, BUMPS_WHEEL_DROPS, BUTTONS, CHARGE_SOURCE, LIGHT_BUMPER, STASIS

unpack_bool_byte = Struct('?').unpack
unpack_byte = Struct('b').unpack
unpack_unsigned_byte = Struct('B').unpack
unpack_short = Struct('>h').unpack
unpack_unsigned_short = Struct('>H').unpack


def binary_response(data):
    return unpack_bool_byte(data)[0]


def packed_binary_response(data):
    return unpack_unsigned_byte(data)[0]


def byte_response(data):
    return unpack_byte(data)[0]


def unsigned_byte_response(data):
    return unpack_unsigned_byte(data)[0]


def short_response(data):
    return unpack_short(data)[0]


def unsigned_short_response(data):
    return unpack_unsigned_short(data)[0]


class PackedBinaryData(object):
    def __init__(self, data):
        self._data = packed_binary_response(data)

    def __bool__(self):
        return self._data != b'\x00'


class BumpsAndWheelDrop(PackedBinaryData):
    def __init__(self, data):
        super(BumpsAndWheelDrop, self).__init__(data)

    @property
    def bump_right(self):
        return bool(self._data & BUMPS_WHEEL_DROPS.BUMP_RIGHT)

    @property
    def bump_left(self):
        return bool(self._data & BUMPS_WHEEL_DROPS.BUMP_LEFT)

    @property
    def wheel_drop_right(self):
        return bool(self._data & BUMPS_WHEEL_DROPS.WHEEL_DROP_RIGHT)

    @property
    def wheel_drop_left(self):
        return bool(self._data & BUMPS_WHEEL_DROPS.WHEEL_DROP_LEFT)


class WheelOvercurrents(PackedBinaryData):
    def __init__(self, data):
        super(WheelOvercurrents, self).__init__(data)

    @property
    def side_brush_overcurrent(self):
        return bool(self._data & WHEEL_OVERCURRENT.SIDE_BRUSH)

    @property
    def main_brush_overcurrent(self):
        return bool(self._data & WHEEL_OVERCURRENT.MAIN_BRUSH)

    @property
    def right_wheel_overcurrent(self):
        return bool(self._data & WHEEL_OVERCURRENT.RIGHT_WHEEL)

    @property
    def left_wheel_overcurrent(self):
        return bool(self._data & WHEEL_OVERCURRENT.LEFT_WHEEL)


class Buttons(PackedBinaryData):
    def __init__(self, data):
        super(Buttons, self).__init__(data)

    @property
    def clean(self):
        return bool(self._data & BUTTONS.CLEAN)

    @property
    def spot(self):
        return bool(self._data & BUTTONS.SPOT)

    @property
    def dock(self):
        return bool(self._data & BUTTONS.DOCK)

    @property
    def minute(self):
        return bool(self._data & BUTTONS.MINUTE)

    @property
    def hour(self):
        return bool(self._data & BUTTONS.HOUR)

    @property
    def day(self):
        return bool(self._data & BUTTONS.DAY)

    @property
    def schedule(self):
        return bool(self._data & BUTTONS.SCHEDULE)

    @property
    def clock(self):
        return bool(self._data & BUTTONS.CLOCK)


class ChargingSources(PackedBinaryData):
    def __init__(self, data):
        super(ChargingSources, self).__init__(data)

    @property
    def internal_charger(self):
        return bool(self._data & CHARGE_SOURCE.INTERNAL)

    @property
    def home_base(self):
        return bool(self._data & CHARGE_SOURCE.HOME_BASE)


class LightBumper(PackedBinaryData):
    def __init__(self, data):
        super(LightBumper, self).__init__(data)

    @property
    def left(self):
        return bool(self._data & LIGHT_BUMPER.LEFT)

    @property
    def front_left(self):
        return bool(self._data & LIGHT_BUMPER.FRONT_LEFT)

    @property
    def center_left(self):
        return bool(self._data & LIGHT_BUMPER.CENTER_LEFT)

    @property
    def center_right(self):
        return bool(self._data & LIGHT_BUMPER.CENTER_RIGHT)

    @property
    def front_right(self):
        return bool(self._data & LIGHT_BUMPER.FRONT_RIGHT)

    @property
    def right(self):
        return bool(self._data & LIGHT_BUMPER.RIGHT)


class Stasis(PackedBinaryData):
    def __init__(self, data):
        super(Stasis, self).__init__(data)

    @property
    def toggling(self):
        return bool(self._data & STASIS.TOGGLING)

    @property
    def disabled(self):
        return bool(self._data & STASIS.DISABLED)


class SensorGroup0(object):
    def __init__(self, data):
        self._data = data
        self._bumps_and_wheel_drops = None
        self._wall_sensor = None
        self._cliff_left_sensor = None
        self._cliff_front_left_sensor = None
        self._cliff_front_right_sensor = None
        self._cliff_right_sensor = None
        self._virtual_wall_sensor = None
        self._wheel_overcurrents = None
        self._dirt_detect_sensor = None
        self._ir_char_omni_sensor = None
        self._buttons = None
        self._distance = None
        self._angle = None
        self._charging_state = None
        self._voltage = None
        self._current = None
        self._temperature = None
        self._battery_charge = None
        self._battery_capacity = None

    @property
    def bumps_and_wheel_drops(self):
        if self._bumps_and_wheel_drops is None:
            self._bumps_and_wheel_drops = BumpsAndWheelDrop(self._data[0:1])
        return self._bumps_and_wheel_drops

    @property
    def wall_sensor(self):
        if self._wall_sensor is None:
            self._wall_sensor = binary_response(self._data[1:2])
        return self._wall_sensor

    @property
    def cliff_left_sensor(self):
        if self._cliff_left_sensor is None:
            self._cliff_left_sensor = binary_response(self._data[2:3])
        return self._cliff_left_sensor

    @property
    def cliff_front_left_sensor(self):
        if self._cliff_front_left_sensor is None:
            self._cliff_front_left_sensor = binary_response(self._data[3:4])
        return self._cliff_front_left_sensor

    @property
    def cliff_front_right_sensor(self):
        if self._cliff_front_right_sensor is None:
            self._cliff_front_right_sensor = binary_response(self._data[4:5])
        return self._cliff_front_right_sensor

    @property
    def cliff_right_sensor(self):
        if self._cliff_right_sensor is None:
            self._cliff_right_sensor = binary_response(self._data[5:6])
        return self._cliff_right_sensor

    @property
    def virtual_wall_sensor(self):
        if self._virtual_wall_sensor is None:
            self._virtual_wall_sensor = binary_response(self._data[6:7])
        return self._virtual_wall_sensor

    @property
    def wheel_overcurrents(self):
        if self._wheel_overcurrents is None:
            self._wheel_overcurrents = WheelOvercurrents(self._data[7:8])
        return self._wheel_overcurrents

    @property
    def dirt_detect_sensor(self):
        if self._dirt_detect_sensor is None:
            self._dirt_detect_sensor = byte_response(self._data[8:9])
        return self._dirt_detect_sensor

    @property
    def ir_char_omni_sensor(self):
        if self._ir_char_omni_sensor is None:
            self._ir_char_omni_sensor = unsigned_byte_response(self._data[10:11])
        return self._ir_char_omni_sensor

    @property
    def buttons(self):
        if self._buttons is None:
            self._buttons = Buttons(self._data[11:12])
        return self._buttons

    @property
    def distance(self):
        if self._distance is None:
            self._distance = short_response(self._data[12:14])
        return self._distance

    @property
    def angle(self):
        if self._angle is None:
            self._angle = short_response(self._data[14:16])
        return self._angle

    @property
    def charging_state(self):
        if self._charging_state is None:
            self._charging_state = unsigned_byte_response(self._data[16:17])
        return self._charging_state

    @property
    def voltage(self):
        if self._voltage is None:
            self._voltage = unsigned_short_response(self._data[17:19])
        return self._voltage

    @property
    def current(self):
        if self._current is None:
            self._current = short_response(self._data[19:21])
        return self._current

    @property
    def temperature(self):
        if self._temperature is None:
            self._temperature = byte_response(self._data[21:22])
        return self._temperature

    @property
    def battery_charge(self):
        if self._battery_charge is None:
            self._battery_charge = unsigned_short_response(self._data[22:24])
        return self._battery_charge

    @property
    def battery_capacity(self):
        if self._battery_capacity is None:
            self._battery_capacity = unsigned_short_response(self._data[24:26])
        return self._battery_capacity


class SensorGroup1(object):
    def __init__(self, data):
        self._data = data
        self._bumps_and_wheel_drops = None
        self._wall_sensor = None
        self._cliff_left_sensor = None
        self._cliff_front_left_sensor = None
        self._cliff_front_right_sensor = None
        self._cliff_right_sensor = None
        self._virtual_wall_sensor = None
        self._wheel_overcurrents = None
        self._dirt_detect_sensor = None

    @property
    def bumps_and_wheel_drops(self):
        if self._bumps_and_wheel_drops is None:
            self._bumps_and_wheel_drops = BumpsAndWheelDrop(self._data[0:1])
        return self._bumps_and_wheel_drops

    @property
    def wall_sensor(self):
        if self._wall_sensor is None:
            self._wall_sensor = binary_response(self._data[1:2])
        return self._wall_sensor

    @property
    def cliff_left_sensor(self):
        if self._cliff_left_sensor is None:
            self._cliff_left_sensor = binary_response(self._data[2:3])
        return self._cliff_left_sensor

    @property
    def cliff_front_left_sensor(self):
        if self._cliff_front_left_sensor is None:
            self._cliff_front_left_sensor = binary_response(self._data[3:4])
        return self._cliff_front_left_sensor

    @property
    def cliff_front_right_sensor(self):
        if self._cliff_front_right_sensor is None:
            self._cliff_front_right_sensor = binary_response(self._data[4:5])
        return self._cliff_front_right_sensor

    @property
    def cliff_right_sensor(self):
        if self._cliff_right_sensor is None:
            self._cliff_right_sensor = binary_response(self._data[5:6])
        return self._cliff_right_sensor

    @property
    def virtual_wall_sensor(self):
        if self._virtual_wall_sensor is None:
            self._virtual_wall_sensor = binary_response(self._data[6:7])
        return self._virtual_wall_sensor

    @property
    def wheel_overcurrents(self):
        if self._wheel_overcurrents is None:
            self._wheel_overcurrents = WheelOvercurrents(self._data[7:8])
        return self._wheel_overcurrents

    @property
    def dirt_detect_sensor(self):
        if self._dirt_detect_sensor is None:
            self._dirt_detect_sensor = byte_response(self._data[8:9])
        return self._dirt_detect_sensor


class SensorGroup2(object):
    def __init__(self, data):
        self._data = data
        self._ir_char_omni_sensor = None
        self._buttons = None
        self._distance = None
        self._angle = None

    @property
    def ir_char_omni_sensor(self):
        if self._ir_char_omni_sensor is None:
            self._ir_char_omni_sensor = unsigned_byte_response(self._data[0:1])
        return self._ir_char_omni_sensor

    @property
    def buttons(self):
        if self._buttons is None:
            self._buttons = Buttons(self._data[1:2])
        return self._buttons

    @property
    def distance(self):
        if self._distance is None:
            self._distance = short_response(self._data[2:4])
        return self._distance

    @property
    def angle(self):
        if self._angle is None:
            self._angle = short_response(self._data[4:6])
        return self._angle


class SensorGroup3(object):
    def __init__(self, data):
        self._data = data
        self._charging_state = None
        self._voltage = None
        self._current = None
        self._temperature = None
        self._battery_charge = None
        self._battery_capacity = None

    @property
    def charging_state(self):
        if self._charging_state is None:
            self._charging_state = unsigned_byte_response(self._data[0:1])
        return self._charging_state

    @property
    def voltage(self):
        if self._voltage is None:
            self._voltage = unsigned_short_response(self._data[1:3])
        return self._voltage

    @property
    def current(self):
        if self._current is None:
            self._current = short_response(self._data[3:5])
        return self._current

    @property
    def temperature(self):
        if self._temperature is None:
            self._temperature = byte_response(self._data[5:6])
        return self._temperature

    @property
    def battery_charge(self):
        if self._battery_charge is None:
            self._battery_charge = unsigned_short_response(self._data[6:8])
        return self._battery_charge

    @property
    def battery_capacity(self):
        if self._battery_capacity is None:
            self._battery_capacity = unsigned_short_response(self._data[8:10])
        return self._battery_capacity


class SensorGroup4(object):
    def __init__(self, data):
        self._data = data
        self._wall_signal = None
        self._cliff_left_signal = None
        self._cliff_front_left_signal = None
        self._cliff_front_right_signal = None
        self._cliff_right_signal = None
        self._charging_sources = None

    @property
    def wall_signal(self):
        if self._wall_signal is None:
            self._wall_signal = unsigned_short_response(self._data[0:2])
        return self._wall_signal

    @property
    def cliff_left_signal(self):
        if self._cliff_left_signal is None:
            self._cliff_left_signal = unsigned_short_response(self._data[2:4])
        return self._cliff_left_signal

    @property
    def cliff_front_left_signal(self):
        if self._cliff_front_left_signal is None:
            self._cliff_front_left_signal = unsigned_short_response(self._data[4:6])
        return self._cliff_front_left_signal

    @property
    def cliff_front_right_signal(self):
        if self._cliff_front_right_signal is None:
            self._cliff_front_right_signal = unsigned_short_response(self._data[6:8])
        return self._cliff_front_right_signal

    @property
    def cliff_right_signal(self):
        if self._cliff_right_signal is None:
            self._cliff_right_signal = unsigned_short_response(self._data[8:10])
        return self._cliff_right_signal

    @property
    def charging_sources(self):
        if self._charging_sources is None:
            self._charging_sources = ChargingSources(self._data[13:14])
        return self._charging_sources


class SensorGroup5(object):
    def __init__(self, data):
        self._data = data
        self._oi_mode = None
        self._song_number = None
        self._is_song_playing = None
        self._number_of_stream_packets = None
        self._requested_velocity = None
        self._requested_radius = None
        self._requested_right_velocity = None
        self._requested_left_velocity = None

    @property
    def oi_mode(self):
        if self._oi_mode is None:
            self._oi_mode = unsigned_byte_response(self._data[0:1])
        return self._oi_mode

    @property
    def song_number(self):
        if self._song_number is None:
            self._song_number = unsigned_byte_response(self._data[1:2])
        return self._song_number

    @property
    def is_song_playing(self):
        if self._is_song_playing is None:
            self._is_song_playing = binary_response(self._data[2:3])
        return self._is_song_playing

    @property
    def number_of_stream_packets(self):
        if self._number_of_stream_packets is None:
            self._number_of_stream_packets = unsigned_byte_response(self._data[3:4])
        return self._number_of_stream_packets

    @property
    def requested_velocity(self):
        if self._requested_velocity is None:
            self._requested_velocity = short_response(self._data[4:6])
        return self._requested_velocity

    @property
    def requested_radius(self):
        if self._requested_radius is None:
            self._requested_radius = short_response(self._data[6:8])
        return self._requested_radius

    @property
    def requested_right_velocity(self):
        if self._requested_right_velocity is None:
            self._requested_right_velocity = short_response(self._data[8:10])
        return self._requested_right_velocity

    @property
    def requested_left_velocity(self):
        if self._requested_left_velocity is None:
            self._requested_left_velocity = short_response(self._data[10:12])
        return self._requested_left_velocity


class SensorGroup6(object):
    def __init__(self, data):
        self._data = data
        self._bumps_and_wheel_drops = None
        self._wall_sensor = None
        self._cliff_left_sensor = None
        self._cliff_front_left_sensor = None
        self._cliff_front_right_sensor = None
        self._cliff_right_sensor = None
        self._virtual_wall_sensor = None
        self._wheel_overcurrents = None
        self._dirt_detect_sensor = None
        self._ir_char_omni_sensor = None
        self._buttons = None
        self._distance = None
        self._angle = None
        self._charging_state = None
        self._voltage = None
        self._current = None
        self._temperature = None
        self._battery_charge = None
        self._battery_capacity = None
        self._wall_signal = None
        self._cliff_left_signal = None
        self._cliff_front_left_signal = None
        self._cliff_front_right_signal = None
        self._cliff_right_signal = None
        self._charging_sources = None
        self._oi_mode = None
        self._song_number = None
        self._is_song_playing = None
        self._number_of_stream_packets = None
        self._requested_velocity = None
        self._requested_radius = None
        self._requested_right_velocity = None
        self._requested_left_velocity = None

    @property
    def bumps_and_wheel_drops(self):
        if self._bumps_and_wheel_drops is None:
            self._bumps_and_wheel_drops = BumpsAndWheelDrop(self._data[0:1])
        return self._bumps_and_wheel_drops

    @property
    def wall_sensor(self):
        if self._wall_sensor is None:
            self._wall_sensor = binary_response(self._data[1:2])
        return self._wall_sensor

    @property
    def cliff_left_sensor(self):
        if self._cliff_left_sensor is None:
            self._cliff_left_sensor = binary_response(self._data[2:3])
        return self._cliff_left_sensor

    @property
    def cliff_front_left_sensor(self):
        if self._cliff_front_left_sensor is None:
            self._cliff_front_left_sensor = binary_response(self._data[3:4])
        return self._cliff_front_left_sensor

    @property
    def cliff_front_right_sensor(self):
        if self._cliff_front_right_sensor is None:
            self._cliff_front_right_sensor = binary_response(self._data[4:5])
        return self._cliff_front_right_sensor

    @property
    def cliff_right_sensor(self):
        if self._cliff_right_sensor is None:
            self._cliff_right_sensor = binary_response(self._data[5:6])
        return self._cliff_right_sensor

    @property
    def virtual_wall_sensor(self):
        if self._virtual_wall_sensor is None:
            self._virtual_wall_sensor = binary_response(self._data[6:7])
        return self._virtual_wall_sensor

    @property
    def wheel_overcurrents(self):
        if self._wheel_overcurrents is None:
            self._wheel_overcurrents = WheelOvercurrents(self._data[7:8])
        return self._wheel_overcurrents

    @property
    def dirt_detect_sensor(self):
        if self._dirt_detect_sensor is None:
            self._dirt_detect_sensor = byte_response(self._data[8:9])
        return self._dirt_detect_sensor

    @property
    def ir_char_omni_sensor(self):
        if self._ir_char_omni_sensor is None:
            self._ir_char_omni_sensor = unsigned_byte_response(self._data[10:11])
        return self._ir_char_omni_sensor

    @property
    def buttons(self):
        if self._buttons is None:
            self._buttons = Buttons(self._data[11:12])
        return self._buttons

    @property
    def distance(self):
        if self._distance is None:
            self._distance = short_response(self._data[12:14])
        return self._distance

    @property
    def angle(self):
        if self._angle is None:
            self._angle = short_response(self._data[14:16])
        return self._angle

    @property
    def charging_state(self):
        if self._charging_state is None:
            self._charging_state = unsigned_byte_response(self._data[16:17])
        return self._charging_state

    @property
    def voltage(self):
        if self._voltage is None:
            self._voltage = unsigned_short_response(self._data[17:19])
        return self._voltage

    @property
    def current(self):
        if self._current is None:
            self._current = short_response(self._data[19:21])
        return self._current

    @property
    def temperature(self):
        if self._temperature is None:
            self._temperature = byte_response(self._data[21:22])
        return self._temperature

    @property
    def battery_charge(self):
        if self._battery_charge is None:
            self._battery_charge = unsigned_short_response(self._data[22:24])
        return self._battery_charge

    @property
    def battery_capacity(self):
        if self._battery_capacity is None:
            self._battery_capacity = unsigned_short_response(self._data[24:26])
        return self._battery_capacity

    @property
    def wall_signal(self):
        if self._wall_signal is None:
            self._wall_signal = unsigned_short_response(self._data[26:28])
        return self._wall_signal

    @property
    def cliff_left_signal(self):
        if self._cliff_left_signal is None:
            self._cliff_left_signal = unsigned_short_response(self._data[28:30])
        return self._cliff_left_signal

    @property
    def cliff_front_left_signal(self):
        if self._cliff_front_left_signal is None:
            self._cliff_front_left_signal = unsigned_short_response(self._data[30:32])
        return self._cliff_front_left_signal

    @property
    def cliff_front_right_signal(self):
        if self._cliff_front_right_signal is None:
            self._cliff_front_right_signal = unsigned_short_response(self._data[32:34])
        return self._cliff_front_right_signal

    @property
    def cliff_right_signal(self):
        if self._cliff_right_signal is None:
            self._cliff_right_signal = unsigned_short_response(self._data[34:36])
        return self._cliff_right_signal

    @property
    def charging_sources(self):
        if self._charging_sources is None:
            self._charging_sources = ChargingSources(self._data[39:40])
        return self._charging_sources

    @property
    def oi_mode(self):
        if self._oi_mode is None:
            self._oi_mode = unsigned_byte_response(self._data[40:41])
        return self._oi_mode

    @property
    def song_number(self):
        if self._song_number is None:
            self._song_number = unsigned_byte_response(self._data[41:42])
        return self._song_number

    @property
    def is_song_playing(self):
        if self._is_song_playing is None:
            self._is_song_playing = binary_response(self._data[42:43])
        return self._is_song_playing

    @property
    def number_of_stream_packets(self):
        if self._number_of_stream_packets is None:
            self._number_of_stream_packets = unsigned_byte_response(self._data[43:44])
        return self._number_of_stream_packets

    @property
    def requested_velocity(self):
        if self._requested_velocity is None:
            self._requested_velocity = short_response(self._data[44:46])
        return self._requested_velocity

    @property
    def requested_radius(self):
        if self._requested_radius is None:
            self._requested_radius = short_response(self._data[46:48])
        return self._requested_radius

    @property
    def requested_right_velocity(self):
        if self._requested_right_velocity is None:
            self._requested_right_velocity = short_response(self._data[48:50])
        return self._requested_right_velocity

    @property
    def requested_left_velocity(self):
        if self._requested_left_velocity is None:
            self._requested_left_velocity = short_response(self._data[50:52])
        return self._requested_left_velocity


class SensorGroup100(object):
    def __init__(self, data):
        self._data = data
        self._bumps_and_wheel_drops = None
        self._wall_sensor = None
        self._cliff_left_sensor = None
        self._cliff_front_left_sensor = None
        self._cliff_front_right_sensor = None
        self._cliff_right_sensor = None
        self._virtual_wall_sensor = None
        self._wheel_overcurrents = None
        self._dirt_detect_sensor = None
        self._ir_char_omni_sensor = None
        self._buttons = None
        self._distance = None
        self._angle = None
        self._charging_state = None
        self._voltage = None
        self._current = None
        self._temperature = None
        self._battery_charge = None
        self._battery_capacity = None
        self._wall_signal = None
        self._cliff_left_signal = None
        self._cliff_front_left_signal = None
        self._cliff_front_right_signal = None
        self._cliff_right_signal = None
        self._charging_sources = None
        self._oi_mode = None
        self._song_number = None
        self._is_song_playing = None
        self._number_of_stream_packets = None
        self._requested_velocity = None
        self._requested_radius = None
        self._requested_right_velocity = None
        self._requested_left_velocity = None
        self._left_encoder_counts = None
        self._right_encoder_counts = None
        self._light_bumper = None
        self._light_bump_left_signal = None
        self._light_bump_front_left_signal = None
        self._light_bump_center_left_signal = None
        self._light_bump_center_right_signal = None
        self._light_bump_front_right_signal = None
        self._light_bump_right_signal = None
        self._ir_character_left = None
        self._ir_character_right = None
        self._left_motor_current = None
        self._right_motor_current = None
        self._main_brush_motor_current = None
        self._side_brush_motor_current = None
        self._stasis = None

    @property
    def bumps_and_wheel_drops(self):
        if self._bumps_and_wheel_drops is None:
            self._bumps_and_wheel_drops = BumpsAndWheelDrop(self._data[0:1])
        return self._bumps_and_wheel_drops

    @property
    def wall_sensor(self):
        if self._wall_sensor is None:
            self._wall_sensor = binary_response(self._data[1:2])
        return self._wall_sensor

    @property
    def cliff_left_sensor(self):
        if self._cliff_left_sensor is None:
            self._cliff_left_sensor = binary_response(self._data[2:3])
        return self._cliff_left_sensor

    @property
    def cliff_front_left_sensor(self):
        if self._cliff_front_left_sensor is None:
            self._cliff_front_left_sensor = binary_response(self._data[3:4])
        return self._cliff_front_left_sensor

    @property
    def cliff_front_right_sensor(self):
        if self._cliff_front_right_sensor is None:
            self._cliff_front_right_sensor = binary_response(self._data[4:5])
        return self._cliff_front_right_sensor

    @property
    def cliff_right_sensor(self):
        if self._cliff_right_sensor is None:
            self._cliff_right_sensor = binary_response(self._data[5:6])
        return self._cliff_right_sensor

    @property
    def virtual_wall_sensor(self):
        if self._virtual_wall_sensor is None:
            self._virtual_wall_sensor = binary_response(self._data[6:7])
        return self._virtual_wall_sensor

    @property
    def wheel_overcurrents(self):
        if self._wheel_overcurrents is None:
            self._wheel_overcurrents = WheelOvercurrents(self._data[7:8])
        return self._wheel_overcurrents

    @property
    def dirt_detect_sensor(self):
        if self._dirt_detect_sensor is None:
            self._dirt_detect_sensor = byte_response(self._data[8:9])
        return self._dirt_detect_sensor

    @property
    def ir_char_omni_sensor(self):
        if self._ir_char_omni_sensor is None:
            self._ir_char_omni_sensor = unsigned_byte_response(self._data[9:10])
        return self._ir_char_omni_sensor

    @property
    def buttons(self):
        if self._buttons is None:
            self._buttons = Buttons(self._data[11:12])
        return self._buttons

    @property
    def distance(self):
        if self._distance is None:
            self._distance = short_response(self._data[12:14])
        return self._distance

    @property
    def angle(self):
        if self._angle is None:
            self._angle = short_response(self._data[14:16])
        return self._angle

    @property
    def charging_state(self):
        if self._charging_state is None:
            self._charging_state = unsigned_byte_response(self._data[16:17])
        return self._charging_state

    @property
    def voltage(self):
        if self._voltage is None:
            self._voltage = unsigned_short_response(self._data[17:19])
        return self._voltage

    @property
    def current(self):
        if self._current is None:
            self._current = short_response(self._data[19:21])
        return self._current

    @property
    def temperature(self):
        if self._temperature is None:
            self._temperature = byte_response(self._data[21:22])
        return self._temperature

    @property
    def battery_charge(self):
        if self._battery_charge is None:
            self._battery_charge = unsigned_short_response(self._data[22:24])
        return self._battery_charge

    @property
    def battery_capacity(self):
        if self._battery_capacity is None:
            self._battery_capacity = unsigned_short_response(self._data[24:26])
        return self._battery_capacity

    @property
    def wall_signal(self):
        if self._wall_signal is None:
            self._wall_signal = unsigned_short_response(self._data[26:28])
        return self._wall_signal

    @property
    def cliff_left_signal(self):
        if self._cliff_left_signal is None:
            self._cliff_left_signal = unsigned_short_response(self._data[28:30])
        return self._cliff_left_signal

    @property
    def cliff_front_left_signal(self):
        if self._cliff_front_left_signal is None:
            self._cliff_front_left_signal = unsigned_short_response(self._data[30:32])
        return self._cliff_front_left_signal

    @property
    def cliff_front_right_signal(self):
        if self._cliff_front_right_signal is None:
            self._cliff_front_right_signal = unsigned_short_response(self._data[32:34])
        return self._cliff_front_right_signal

    @property
    def cliff_right_signal(self):
        if self._cliff_right_signal is None:
            self._cliff_right_signal = unsigned_short_response(self._data[34:36])
        return self._cliff_right_signal

    @property
    def charging_sources(self):
        if self._charging_sources is None:
            self._charging_sources = ChargingSources(self._data[39:40])
        return self._charging_sources

    @property
    def oi_mode(self):
        if self._oi_mode is None:
            self._oi_mode = unsigned_byte_response(self._data[40:41])
        return self._oi_mode

    @property
    def song_number(self):
        if self._song_number is None:
            self._song_number = unsigned_byte_response(self._data[41:42])
        return self._song_number

    @property
    def is_song_playing(self):
        if self._is_song_playing is None:
            self._is_song_playing = binary_response(self._data[42:43])
        return self._is_song_playing

    @property
    def number_of_stream_packets(self):
        if self._number_of_stream_packets is None:
            self._number_of_stream_packets = unsigned_byte_response(self._data[43:44])
        return self._number_of_stream_packets

    @property
    def requested_velocity(self):
        if self._requested_velocity is None:
            self._requested_velocity = short_response(self._data[44:46])
        return self._requested_velocity

    @property
    def requested_radius(self):
        if self._requested_radius is None:
            self._requested_radius = short_response(self._data[46:48])
        return self._requested_radius

    @property
    def requested_right_velocity(self):
        if self._requested_right_velocity is None:
            self._requested_right_velocity = short_response(self._data[48:50])
        return self._requested_right_velocity

    @property
    def requested_left_velocity(self):
        if self._requested_left_velocity is None:
            self._requested_left_velocity = short_response(self._data[50:52])
        return self._requested_left_velocity

    @property
    def left_encoder_counts(self):
        if self._left_encoder_counts is None:
            self._left_encoder_counts = unsigned_short_response(self._data[52:54])
        return self._left_encoder_counts

    @property
    def right_encoder_counts(self):
        if self._right_encoder_counts is None:
            self._right_encoder_counts = unsigned_short_response(self._data[54:56])
        return self._right_encoder_counts

    @property
    def light_bumper(self):
        if self._light_bumper is None:
            self._light_bumper = LightBumper(self._data[56:57])
        return self._light_bumper

    @property
    def light_bump_left_signal(self):
        if self._light_bump_left_signal is None:
            self._light_bump_left_signal = unsigned_short_response(self._data[57:59])
        return self._light_bump_left_signal

    @property
    def light_bump_front_left_signal(self):
        if self._light_bump_front_left_signal is None:
            self._light_bump_front_left_signal = unsigned_short_response(self._data[59:61])
        return self._light_bump_front_left_signal

    @property
    def light_bump_center_left_signal(self):
        if self._light_bump_center_left_signal is None:
            self._light_bump_center_left_signal = unsigned_short_response(self._data[61:63])
        return self._light_bump_center_left_signal

    @property
    def light_bump_center_right_signal(self):
        if self._light_bump_center_right_signal is None:
            self._light_bump_center_right_signal = unsigned_short_response(self._data[63:65])
        return self._light_bump_center_right_signal

    @property
    def light_bump_front_right_signal(self):
        if self._light_bump_front_right_signal is None:
            self._light_bump_front_right_signal = unsigned_short_response(self._data[65:67])
        return self._light_bump_front_right_signal

    @property
    def light_bump_right_signal(self):
        if self._light_bump_right_signal is None:
            self._light_bump_right_signal = unsigned_short_response(self._data[67:69])
        return self._light_bump_right_signal

    @property
    def ir_character_left(self):
        if self._ir_character_left is None:
            self._ir_character_left = unsigned_byte_response(self._data[69:70])
        return self._ir_character_left

    @property
    def ir_character_right(self):
        if self._ir_character_right is None:
            self._ir_character_right = unsigned_byte_response(self._data[70:71])
        return self._ir_character_right

    @property
    def left_motor_current(self):
        if self._left_motor_current is None:
            self._left_motor_current = short_response(self._data[71:73])
        return self._left_motor_current

    @property
    def right_motor_current(self):
        if self._right_motor_current is None:
            self._right_motor_current = short_response(self._data[73:75])
        return self._right_motor_current

    @property
    def main_brush_motor_current(self):
        if self._main_brush_motor_current is None:
            self._main_brush_motor_current = short_response(self._data[75:77])
        return self._main_brush_motor_current

    @property
    def side_brush_motor_current(self):
        if self._side_brush_motor_current is None:
            self._side_brush_motor_current = short_response(self._data[77:79])
        return self._side_brush_motor_current

    @property
    def stasis(self):
        if self._stasis is None:
            self._stasis = Stasis(self._data[79:80])
        return self._stasis


class SensorGroup101(object):
    def __init__(self, data):
        self._data = data
        self._left_encoder_counts = None
        self._right_encoder_counts = None
        self._light_bumper = None
        self._light_bump_left_signal = None
        self._light_bump_front_left_signal = None
        self._light_bump_center_left_signal = None
        self._light_bump_center_right_signal = None
        self._light_bump_front_right_signal = None
        self._light_bump_right_signal = None
        self._ir_character_left = None
        self._ir_character_right = None
        self._left_motor_current = None
        self._right_motor_current = None
        self._main_brush_motor_current = None
        self._side_brush_motor_current = None
        self._stasis = None

    @property
    def left_encoder_counts(self):
        if self._left_encoder_counts is None:
            self._left_encoder_counts = unsigned_short_response(self._data[0:2])
        return self._left_encoder_counts

    @property
    def right_encoder_counts(self):
        if self._right_encoder_counts is None:
            self._right_encoder_counts = unsigned_short_response(self._data[2:4])
        return self._right_encoder_counts

    @property
    def light_bumper(self):
        if self._light_bumper is None:
            self._light_bumper = LightBumper(self._data[4:5])
        return self._light_bumper

    @property
    def light_bump_left_signal(self):
        if self._light_bump_left_signal is None:
            self._light_bump_left_signal = unsigned_short_response(self._data[5:7])
        return self._light_bump_left_signal

    @property
    def light_bump_front_left_signal(self):
        if self._light_bump_front_left_signal is None:
            self._light_bump_front_left_signal = unsigned_short_response(self._data[7:9])
        return self._light_bump_front_left_signal

    @property
    def light_bump_center_left_signal(self):
        if self._light_bump_center_left_signal is None:
            self._light_bump_center_left_signal = unsigned_short_response(self._data[9:11])
        return self._light_bump_center_left_signal

    @property
    def light_bump_center_right_signal(self):
        if self._light_bump_center_right_signal is None:
            self._light_bump_center_right_signal = unsigned_short_response(self._data[11:13])
        return self._light_bump_center_right_signal

    @property
    def light_bump_front_right_signal(self):
        if self._light_bump_front_right_signal is None:
            self._light_bump_front_right_signal = unsigned_short_response(self._data[13:15])
        return self._light_bump_front_right_signal

    @property
    def light_bump_right_signal(self):
        if self._light_bump_right_signal is None:
            self._light_bump_right_signal = unsigned_short_response(self._data[15:17])
        return self._light_bump_right_signal

    @property
    def ir_character_left(self):
        if self._ir_character_left is None:
            self._ir_character_left = unsigned_byte_response(self._data[17:18])
        return self._ir_character_left

    @property
    def ir_character_right(self):
        if self._ir_character_right is None:
            self._ir_character_right = unsigned_byte_response(self._data[18:19])
        return self._ir_character_right

    @property
    def left_motor_current(self):
        if self._left_motor_current is None:
            self._left_motor_current = short_response(self._data[19:21])
        return self._left_motor_current

    @property
    def right_motor_current(self):
        if self._right_motor_current is None:
            self._right_motor_current = short_response(self._data[21:23])
        return self._right_motor_current

    @property
    def main_brush_motor_current(self):
        if self._main_brush_motor_current is None:
            self._main_brush_motor_current = short_response(self._data[23:25])
        return self._main_brush_motor_current

    @property
    def side_brush_motor_current(self):
        if self._side_brush_motor_current is None:
            self._side_brush_motor_current = short_response(self._data[25:27])
        return self._side_brush_motor_current

    @property
    def stasis(self):
        if self._stasis is None:
            self._stasis = Stasis(self._data[27:28])
        return self._stasis


class SensorGroup106(object):
    def __init__(self, data):
        self._data = data
        self._light_bump_left_signal = None
        self._light_bump_front_left_signal = None
        self._light_bump_center_left_signal = None
        self._light_bump_center_right_signal = None
        self._light_bump_front_right_signal = None
        self._light_bump_right_signal = None

    @property
    def light_bump_left_signal(self):
        if self._light_bump_left_signal is None:
            self._light_bump_left_signal = unsigned_short_response(self._data[0:2])
        return self._light_bump_left_signal

    @property
    def light_bump_front_left_signal(self):
        if self._light_bump_front_left_signal is None:
            self._light_bump_front_left_signal = unsigned_short_response(self._data[2:4])
        return self._light_bump_front_left_signal

    @property
    def light_bump_center_left_signal(self):
        if self._light_bump_center_left_signal is None:
            self._light_bump_center_left_signal = unsigned_short_response(self._data[4:6])
        return self._light_bump_center_left_signal

    @property
    def light_bump_center_right_signal(self):
        if self._light_bump_center_right_signal is None:
            self._light_bump_center_right_signal = unsigned_short_response(self._data[6:8])
        return self._light_bump_center_right_signal

    @property
    def light_bump_front_right_signal(self):
        if self._light_bump_front_right_signal is None:
            self._light_bump_front_right_signal = unsigned_short_response(self._data[8:10])
        return self._light_bump_front_right_signal

    @property
    def light_bump_right_signal(self):
        if self._light_bump_right_signal is None:
            self._light_bump_right_signal = unsigned_short_response(self._data[10:12])
        return self._light_bump_right_signal


class SensorGroup107(object):
    def __init__(self, data):
        self._data = data
        self._left_motor_current = None
        self._right_motor_current = None
        self._main_brush_motor_current = None
        self._side_brush_motor_current = None
        self._stasis = None

    @property
    def left_motor_current(self):
        if self._left_motor_current is None:
            self._left_motor_current = short_response(self._data[0:2])
        return self._left_motor_current

    @property
    def right_motor_current(self):
        if self._right_motor_current is None:
            self._right_motor_current = short_response(self._data[2:4])
        return self._right_motor_current

    @property
    def main_brush_motor_current(self):
        if self._main_brush_motor_current is None:
            self._main_brush_motor_current = short_response(self._data[4:6])
        return self._main_brush_motor_current

    @property
    def side_brush_motor_current(self):
        if self._side_brush_motor_current is None:
            self._side_brush_motor_current = short_response(self._data[6:8])
        return self._side_brush_motor_current

    @property
    def stasis(self):
        if self._stasis is None:
            self._stasis = Stasis(self._data[8:9])
        return self._stasis
