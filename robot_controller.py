import irobot.robots.create2 as crt2
import irobot.openinterface.constants as roboconsts
import numpy as np
import math
import glob
import time

import measurement_params as parameters
import measurement_utils as utils


class RobotInitError(Exception):
    pass


class RobotController(object):
    def __init__(self):
        self.logger = utils.init_logger('RobotController')

        # determine correct port to connect to
        this_os = utils.get_operating_system()
        if this_os == 'linux':
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif this_os == 'mac':
            ports = glob.glob('/dev/tty.*')
        else:
            self.logger.error('Unsupported platform.')
            raise SystemExit('This platform is not supported yet.')
        usb_port_idx = [i for i, x in enumerate([port.lower().find('usb') for port in ports]) if x > 0]

        try:
            # init robot
            self.port = ports[usb_port_idx[0]]

            self.rob = crt2.Create2(self.port)
        except Exception as e:
            self.logger.error('The robot could not be initialized. Try to replug the usb connection or turn on the '
                              'robot.')
            raise RobotInitError('The robot could not be initialized. Try to replug the usb connection or '
                                 'turn on the robot.') from e

        self.logger.info('Initialized the robot successfully.')

    def start_robot(self):
        # start the robot
        if self.rob.oi_mode == roboconsts.MODES.OFF:
            self.rob.start()
            self.logger.info('Started the robot successfully.')
        else:
            self.logger.info('Robot is already turned on.')

        # get into safe mode (i.e. programmable, but still active sensors = you cannot crash the robot)
        # self.rob.oi_mode = roboconsts.MODES.SAFE
        self.rob.oi_mode = roboconsts.MODES.FULL
        self.logger.info('Robot is now in full mode.')

    def _get_angle(self):
        """
        Implementation of get_angle is wrong in Roomba firmware. Therefore, angle has to be calculated over other
        sensors. For more information check those links:
        https://robotics.stackexchange.com/questions/7062/create2-angle-packet-id-20
        https://robotics.stackexchange.com/questions/7121/irobot-create-2-angle-measurement

        TODO: Firmware update, so this becomes obsolete
        """
        dist_left_wheel = self.rob.left_encoder_counts * (1 / 508.8) * (math.pi * 72)
        dist_right_wheel = self.rob.right_encoder_counts * (1 / 508.8) * (math.pi * 72)
        angle = ((dist_right_wheel - dist_left_wheel) / 235) * 180 / math.pi
        return angle

    def _get_straight_distance(self):
        """
        Implementation of get_distance is wrong in Roomba firmware. Therefore, angle has to be calculated over other
        sensors. For more information check those links:
        https://robotics.stackexchange.com/questions/7062/create2-angle-packet-id-20
        https://robotics.stackexchange.com/questions/7121/irobot-create-2-angle-measurement

        TODO: Firmware update, so this becomes obsolete
        """
        distance = self.rob.left_encoder_counts * (1 / 508.8) * (math.pi * 72)
        return distance

    def has_hit_obstacle(self):
        try:
            bd = self.rob.bumps_and_wheel_drops

            if bd.bump_left:
                # This sensor seems to fire when the loose plastic part in front of Roomba is hit on left
                self.logger.info('Left bump sensor activated.')
                return True
            elif bd.bump_right:
                # This sensor seems to fire when the loose plastic part in front of Roomba is hit on right
                self.logger.info('Right bump sensor activated.')
                return True
            else:
                return False
        except:
            self.logger.info('There was a problem with determining the sensor state. The robot might have '
                             'disconnected.')
            if self.rob.oi_mode == roboconsts.MODES.OFF:
                self.logger.info('Robot was turned off, so I will start it again.')
                self.rob.start()
            self.rob.oi_mode = roboconsts.MODES.FULL
            return True

    def _spin_timed(self, t_interval, speed=parameters.SPEED_SPIN, ignore_obstacles=False):
        """
        :param t_interval: time interval that the spin should last [in seconds]
        :param speed: speed of the rotation, positive values are for counterclockwise rotations and negative values are
        for clockwise rotations [in mm/s]
        :param ignore_obstacles: ignores obstacle sensors. Useful for example, if robot has hit an obstacle before: the
        sensors will still fire and have to be ignored during the reversal of the movement
        :return the first return of this function is True when the movement was performed without hitting obstacles. If
        an obstacle was hit, the second return specifies the time interval after which it was hit. The returned time can
        subsequently be used to reverse the movement.
        """
        obstacle_hit = False
        time_when_hit = []

        t_end = time.time() + t_interval

        # start spinning with given speed
        if speed >= 0:
            self.rob.spin_left(speed)
        else:
            self.rob.spin_right(abs(speed))

        # keep spinning for specified time interval or until obstacle is hit
        while time.time() < t_end:
            obstacle_hit = self.has_hit_obstacle()
            if obstacle_hit and not ignore_obstacles:
                self.logger.debug('Obstacle was hit. Will stop the spin now.')
                time_when_hit = time.time() - (t_end - t_interval)
                break

        # stop movement
        self.rob.drive_straight(0)

        return (not obstacle_hit), time_when_hit

    def _spin_angle(self, angle, speed=parameters.SPEED_SPIN, ignore_obstacles=False):
        """
        :param angle: angle of the desired rotation [in degrees]
        :param speed: speed of the rotation, positive values are for counterclockwise rotations and negative
        values are for clockwise rotations [in mm/s]
        :param ignore_obstacles: ignores obstacle sensors. Useful for example, if robot has hit an obstacle before: the
        sensors will still fire and have to be ignored during the reversal of the movement
        :return the first return of this function is True when the movement was performed without hitting obstacles. If
        an obstacle was hit, the second return specifies the angle the robot was already spinning before the obstacle.
        The returned angle can subsequently be used to reverse the movement.
        """
        # get initial angle to calculate the difference later
        start_angle = self._get_angle()

        obstacle_hit = False
        angle_when_hit = []

        # start spinning with given speed
        if speed >= 0:
            self.rob.spin_left(speed)
        else:
            self.rob.spin_right(abs(speed))

        # keep spinning until angle difference is reached or an obstacle is hit
        # TODO: the angle "measurement" is not really accurate, is there a better way?
        while abs(self._get_angle() - start_angle) < angle:
            obstacle_hit = self.has_hit_obstacle()
            if obstacle_hit and not ignore_obstacles:
                angle_when_hit = abs(self._get_angle() - start_angle)
                break

        # stop movement
        self.rob.drive_straight(0)

        return (not obstacle_hit), angle_when_hit

    def _drive_straight_timed(self, t_interval, speed=parameters.SPEED_MOVE, ignore_obstacles=False):
        """
        :param t_interval: time interval that the robot should drive straight [in seconds]
        :param speed: speed of the rotation [in mm/s]
        :param ignore_obstacles: ignores obstacle sensors. Useful for example, if robot has hit an obstacle before: the
        sensors will still fire and have to be ignored during the reversal of the movement
        :return the first return of this function is True when the movement was performed without hitting obstacles. If
        an obstacle was hit, the second return specifies the time interval after which it was hit. The returned time can
        subsequently be used to reverse the movement.
        """
        if speed < 0:
            speed = max(speed, -parameters.SPEED_MOVE)  # limit speed, because there is no backwards wall sensor

        obstacle_hit = False
        time_when_hit = []

        t_end = time.time() + t_interval

        # start driving with given speed
        self.rob.drive_straight(speed)

        # keep driving for specified time interval or until an obstacle is hit
        while time.time() < t_end:
            obstacle_hit = self.has_hit_obstacle()
            if obstacle_hit and not ignore_obstacles:
                self.logger.debug('Obstacle was hit. Will stop the drive now.')
                time_when_hit = time.time() - (t_end - t_interval)
                break

        # stop movement
        self.rob.drive_straight(0)

        return (not obstacle_hit), time_when_hit

    def _drive_straight_distance(self, distance, speed=parameters.SPEED_MOVE, ignore_obstacles=False):
        """
        :param distance: distance that the robot should drive straight [in mm]
        :param speed: speed of the movement [in mm/s]
        :param ignore_obstacles: ignores obstacle sensors. Useful for example, if robot has hit an obstacle before: the
        sensors will still fire and have to be ignored during the reversal of the movement
        :return the first return of this function is True when the movement was performed without hitting obstacles. If
        an obstacle was hit, the second return specifies the distance the robot was already spinning before the
        obstacle. The returned distance can subsequently be used to reverse the movement.
        """
        if speed < 0:
            speed = max(speed, -parameters.SPEED_MOVE)  # limit speed to 150, because there is no backwards wall sensor

        self.logger.info('Driving straight for {:.3f} m with a speed of {} mm/s.'.format(distance, speed))
        obstacle_hit = False
        distance_when_hit = []

        start_distance = self._get_straight_distance()

        # start driving with given speed
        self.rob.drive_straight(speed)

        # keep driving until specified distance is reached or until an obstacle is hit
        while abs(self._get_straight_distance() - start_distance) < distance:
            obstacle_hit = self.has_hit_obstacle()
            if obstacle_hit and not ignore_obstacles:
                distance_when_hit = abs(self._get_straight_distance() - start_distance)
                break

        # stop movement
        self.rob.drive_straight(0)

        return (not obstacle_hit), distance_when_hit

    def _drive_circle_timed(self, t_interval, radius=10, speed=parameters.SPEED_MOVE, ignore_obstacles=False):
        """
        TODO: Behaviour of this function is still a little dubious.
        :param t_interval: time interval that the robot should drive on the arc [in seconds]
        :param radius: radius of the circle that the robot should drive on [in mm]
        :param speed: speed of the rotation [in mm/s]
        :param ignore_obstacles: ignores obstacle sensors. Useful for example, if robot has hit an obstacle before: the
        sensors will still fire and have to be ignored during the reversal of the movement
        :return the first return of this function is True when the movement was performed without hitting obstacles. If
        an obstacle was hit, the second return specifies the time interval after which it was hit. The returned time can
        subsequently be used to reverse the movement.
        """
        if speed < 0:
            speed = max(speed, -parameters.SPEED_MOVE)  # limit speed to 150, because there is no backwards wall sensor

        obstacle_hit = False
        time_when_hit = []

        t_end = time.time() + t_interval

        # start driving on specified circle with specified speed
        self.rob.drive(speed, radius)

        # keep driving for specified time interval or until obstacle is hit
        while time.time() < t_end:
            obstacle_hit = self.has_hit_obstacle()
            if obstacle_hit and not ignore_obstacles:
                time_when_hit = time.time() - (t_end - t_interval)
                break

        # stop movement
        self.rob.drive_straight(0)

        return (not obstacle_hit), time_when_hit

    def move_robot_randomly(self):
        # Determine a random spin time
        random_spin_time = np.random.uniform(parameters.MIN_RAND_SPIN_TIME, parameters.MAX_RAND_SPIN_TIME)
        self.logger.info('Random spin time: {:.3f}'.format(random_spin_time))

        # Spin robot for that time
        spin_successful, time_when_hit = self._spin_timed(random_spin_time, parameters.SPEED_SPIN)

        if not spin_successful:
            time.sleep(1)
            self._drive_straight_timed(1, -1 * parameters.SPEED_MOVE, ignore_obstacles=True)

        # Determine a random drive time
        random_drive_time = np.random.uniform(parameters.MIN_RAND_DRIVE_TIME, parameters.MAX_RAND_DRIVE_TIME)
        self.logger.info('Random drive time: {:.3f}'.format(random_drive_time))

        # Move forward for a random time
        move_successful, time_when_hit = self._drive_straight_timed(random_drive_time, parameters.SPEED_MOVE)

        if not move_successful:
            time.sleep(1)
            time_to_drive_backwards = np.min([3, random_drive_time])
            self._drive_straight_timed(time_to_drive_backwards, -1 * parameters.SPEED_MOVE, ignore_obstacles=True)

    def move_robot_straight(self, distance, backwards=False):
        if not backwards:
            self.logger.info('{} m long straight forward movement of the robot was initiated.'.format(distance))
            speed = parameters.SPEED_MOVE
        else:
            self.logger.info('{} m long straight backward movement of the robot was initiated.'.format(distance))
            speed = parameters.SPEED_MOVE * -1

        distance = distance * 1000  # convert from meters into millimeters

        # move robot
        move_successful, distance_when_hit = self._drive_straight_distance(distance, speed)

        if not move_successful:
            self.logger.info('Obstacle was hit. Therefore the robot will move back to its original position.')
            time.sleep(1)
            self._drive_straight_distance(distance_when_hit, -1 * speed, ignore_obstacles=True)

    def spin_robot(self, angle, clockwise=False):
        if not clockwise:
            self.logger.info('{} degree counterclockwise spin of robot was initiated.'.format(angle))
            speed_spin = parameters.SPEED_SPIN
        else:
            self.logger.info('{} degree clockwise spin of the robot was initiated.'.format(angle))
            speed_spin = parameters.SPEED_SPIN * -1

        # spin robot
        move_succesful, angle_when_hit = self._spin_angle(angle, speed_spin)

        if not move_succesful:
            self.logger.info('Obstacle was hit. Therefore the robot will move back to its original position.')
            time.sleep(1)
            self._spin_angle(angle_when_hit, -1 * speed_spin, ignore_obstacles=True)

    def play_glorienttes_song(self):
        self.logger.info('I\'m now singing you the song of my people.')
        self.rob.set_song(0, [[69, 10], [71, 10], [74, 10], [71, 10], [78, 20], [78, 20], [76, 30]])
        self.rob.play_song(0)
        time.sleep(2)

        self.rob.set_song(1, [[69, 10], [71, 10], [74, 10], [71, 10], [76, 20], [76, 20], [74, 20], [73, 5], [71, 5]])
        self.rob.play_song(1)
        time.sleep(2)

        self.rob.set_song(2, [[69, 10], [71, 10], [74, 10], [71, 10], [74, 20], [76, 10], [73, 20], [69, 20], [69, 10],
                              [76, 20],
                              [74, 20]])
        self.rob.play_song(2)
