__author__ = 'Matthew Witherwax (lemoneer)'

from struct import Struct, pack

from .constants import DAYS, MOTORS, LEDS, BUTTONS, DRIVE, WEEKDAY_LEDS, SCHEDULING_LEDS

pack_op_code = Struct('B').pack
# note all the packs below include a leading byte for the op code
# for instance, pack_signed_byte actually packs two bytes - the
# op code and the data byte
pack_signed_byte = Struct('Bb').pack
pack_unsigned_byte = Struct('B' * 2).pack
pack_2unsigned_bytes = Struct('B' * 3).pack
pack_3signed_bytes = Struct('B' + 'b' * 3).pack
pack_3unsigned_bytes = Struct('B' * 4).pack
pack_4unsigned_bytes = Struct('B' * 5).pack
pack_schedule = Struct('B' + 'b' * 15).pack
pack_drive = Struct('>Bhh').pack
pack_drive_special_cases = Struct('>BhH').pack


def start():
    return pack_op_code(128)


def reset():
    return pack_op_code(7)


def stop():
    return pack_op_code(173)


def set_baud(baud):
    return pack_signed_byte(129, baud)


set_mode_passive = start


def set_mode_safe():
    return pack_op_code(131)


def set_mode_full():
    return pack_op_code(132)


def clean():
    return pack_op_code(135)


def clean_max():
    return pack_op_code(136)


def clean_spot():
    return pack_op_code(134)


def seek_dock():
    return pack_op_code(143)


def power_down():
    return pack_op_code(133)


def get_days(sun_hour, sun_min, mon_hour, mon_min, tues_hour, tues_min, wed_hour, wed_min, thurs_hour, thurs_min,
             fri_hour, fri_min, sat_hour, sat_min):
    days = 0
    if sun_hour != 0 or sun_min != 0:
        days |= DAYS.SUNDAY
    if mon_hour != 0 or mon_min != 0:
        days |= DAYS.MONDAY
    if tues_hour != 0 or tues_min != 0:
        days |= DAYS.TUESDAY
    if wed_hour != 0 or wed_min != 0:
        days |= DAYS.WEDNESDAY
    if thurs_hour != 0 or thurs_min != 0:
        days |= DAYS.THURSDAY
    if fri_hour != 0 or fri_min != 0:
        days |= DAYS.FRIDAY
    if sat_hour != 0 or sat_min != 0:
        days |= DAYS.SATURDAY
    return days


def set_schedule(sun_hour, sun_min, mon_hour, mon_min, tues_hour, tues_min, wed_hour, wed_min, thurs_hour, thurs_min,
                 fri_hour, fri_min, sat_hour, sat_min):
    days = get_days(sun_hour, sun_min, mon_hour, mon_min, tues_hour, tues_min, wed_hour, wed_min, thurs_hour, thurs_min,
                    fri_hour, fri_min, sat_hour, sat_min)
    return pack_schedule(167, days, sun_hour, sun_min, mon_hour, mon_min, tues_hour, tues_min, wed_hour, wed_min,
                         thurs_hour, thurs_min, fri_hour, fri_min, sat_hour, sat_min)


def set_day_time(day=0, hour=0, minute=0):
    return pack_3signed_bytes([168, day, hour, minute])


def drive(velocity, radius):
    if radius == DRIVE.STRAIGHT or radius == DRIVE.TURN_IN_PLACE_CW or radius == DRIVE.TURN_IN_PLACE_CCW:
        return pack_drive_special_cases(137, velocity, radius)
    return pack_drive(137, velocity, radius)


def drive_direct(right_velocity, left_velocity):
    return pack_drive(145, right_velocity, left_velocity)


def drive_pwm(right_pwm, left_pwm):
    return pack_drive(146, right_pwm, left_pwm)


def set_motors(main_brush_on, main_brush_reverse, side_brush, side_brush_reverse, vacuum):
    motors = 0
    if main_brush_on:
        motors |= MOTORS.MAIN_BRUSH
    if main_brush_reverse:
        motors |= MOTORS.MAIN_BRUSH_DIRECTION
    if side_brush:
        motors |= MOTORS.SIDE_BRUSH
    if side_brush_reverse:
        motors |= MOTORS.SIDE_BRUSH_DIRECTION
    if vacuum:
        motors |= MOTORS.SIDE_VACUUM

    return pack_signed_byte(138, motors)


def set_motors_pwm(main_brush_pwm, side_brush_pwm, vacuum_pwm):
    return pack_3signed_bytes(144, main_brush_pwm, side_brush_pwm, vacuum_pwm)


def set_leds(debris, spot, dock, check_robot, power_color, power_intensity):
    leds = 0
    if debris:
        leds |= LEDS.DEBRIS
    if spot:
        leds |= LEDS.SPOT
    if dock:
        leds |= LEDS.DOCK
    if check_robot:
        leds |= LEDS.CHECK_ROBOT

    return pack_3unsigned_bytes(139, leds, power_color, power_intensity)


def set_scheduling_leds(sun, mon, tues, wed, thurs, fri, sat, schedule, clock, am, pm, colon):
    weekday_leds = 0
    if sun:
        weekday_leds |= WEEKDAY_LEDS.SUNDAY
    if mon:
        weekday_leds |= WEEKDAY_LEDS.MONDAY
    if tues:
        weekday_leds |= WEEKDAY_LEDS.TUESDAY
    if wed:
        weekday_leds |= WEEKDAY_LEDS.WEDNESDAY
    if thurs:
        weekday_leds |= WEEKDAY_LEDS.THURSDAY
    if fri:
        weekday_leds |= WEEKDAY_LEDS.FRIDAY
    if sat:
        weekday_leds |= WEEKDAY_LEDS.SATURDAY

    scheduling_leds = 0
    if schedule:
        scheduling_leds |= SCHEDULING_LEDS.SCHEDULE
    if clock:
        scheduling_leds |= SCHEDULING_LEDS.CLOCK
    if am:
        scheduling_leds |= SCHEDULING_LEDS.AM
    if pm:
        scheduling_leds |= SCHEDULING_LEDS.PM
    if colon:
        scheduling_leds |= SCHEDULING_LEDS.COLON

    return pack_2unsigned_bytes(162, weekday_leds, scheduling_leds)


def set_raw_leds(digit1, digit2, digit3, digit4):
    return pack_4unsigned_bytes(163, digit4, digit3, digit2, digit1)


def trigger_buttons(clean, spot, dock, minute, hour, day, schedule, clock):
    buttons = 0
    if clean:
        buttons |= BUTTONS.CLEAN
    if spot:
        buttons |= BUTTONS.SPOT
    if dock:
        buttons |= BUTTONS.DOCK
    if minute:
        buttons |= BUTTONS.MINUTE
    if hour:
        buttons |= BUTTONS.HOUR
    if day:
        buttons |= BUTTONS.DAY
    if schedule:
        buttons |= BUTTONS.SCHEDULE
    if clock:
        buttons |= BUTTONS.CLOCK

    return pack_unsigned_byte(165, buttons)


def set_ascii_leds(char1, char2, char3, char4):
    return pack_4unsigned_bytes(164, char1, char2, char3, char4)


def set_song(song_number, notes):
    num_notes = len(notes)

    note_data = [0] * (3 + num_notes * 2)
    note_data[0] = 140
    note_data[1] = song_number
    note_data[2] = num_notes

    for i in range(0, num_notes):
        note = notes[i]
        note_idx = i * 2
        note_data[note_idx + 3] = note[0]
        note_data[note_idx + 4] = note[1]

    return pack('%sB' % len(note_data), *note_data)


def play_song(song_number):
    return pack_unsigned_byte(141, song_number)


def request_sensor_data(packet_id):
    return pack_unsigned_byte(142, packet_id)
