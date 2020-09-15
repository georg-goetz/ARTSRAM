import socket
import _socket
import re
import pathlib
import threading

import robot_controller as robcon
import robot_commands as robcmd

import sweep_measurement as sweep

import measurement_params as parameters
import measurement_utils as utils

import time


class RobotServer(socket.socket):
    def __init__(self, connected_init=False, family=socket.AF_INET, socket_type=socket.SOCK_STREAM, *args, **kwargs):
        if not connected_init:
            self.logger = utils.init_logger('RobotServer')
        else:
            self.logger = utils.get_logger('RobotServer')

        super().__init__(family=family, type=socket_type, *args, **kwargs)

        self.init_robot = parameters.INIT_ROBOT

        # a robot controller and sweep controller should only be created if a client connects to the server
        if connected_init:
            # a robot controller should only be created if the user wishes to init a robot
            if self.init_robot:
                self.rob = robcon.RobotController()

            self.sweep_controller = sweep.SweepMeasurement(nfft=parameters.SWEEP_LENGTH * parameters.SWEEP_FS,
                                                           fs=parameters.SWEEP_FS)

        self.logger.info('Successfully initialized a RobotServer.')

    @classmethod
    # This is method required in order to convert a socket into an RobotServer (e.g. after accept() returns socket)
    def copy(cls, sock):
        fd = _socket.dup(sock.fileno())
        # here we create an RobotServer and pass the arguments of the original socket
        copy = cls(connected_init=True, family=sock.family, socket_type=sock.type, proto=sock.proto, fileno=fd)
        copy.settimeout(sock.gettimeout())

        # close original socket
        sock.close()

        return copy

    def wait_for_connection(self, host_address=parameters.IP_RASPBERRY1, port=parameters.STANDARD_ROBOT_PORT):
        self.bind((host_address, port))
        self.listen()
        conn, addr = self.accept()
        self.logger.info('Client connected to the RoboServer: {}'.format(addr))

        # convert Socket into RoboSocket
        conn = self.copy(conn)
        return conn

    def start_receiver_loop(self):
        with self:
            self.logger.info('Started RobotServer receiver loop.')
            while True:
                data = self.recv(1024)
                if not data:  # break loop as soon as client is closed (then client sends empty data)
                    break
                else:
                    try:
                        self.process_command(data)
                    except robcon.RobotInitError:
                        if self.init_robot:
                            raise
                    except ValueError:
                        break

    def acknowledge_action_complete(self):
        command = robcmd.ACK.encode('utf-8')
        self.sendall(command)

    def process_command(self, data):
        data = data.decode('utf-8')
        self.logger.info('RobotServer received the following command: ' + data)

        # split received data into the following parts: (command type: robot or evoke)_(command)_(numerical params)
        regex_obj = re.match(r'([rem])_([\D\d]+)', data)
        command_type = regex_obj.group(1)
        command = regex_obj.group(2)

        self.logger.info('Disassembled the command into the following parts. Command type=\"{}\", '
                         'command=\"{}\".'.format(command_type, command))

        if command_type == robcmd.TYPE_ROBOT:
            self.process_robot_command(command)
        elif command_type == robcmd.TYPE_META:
            self.process_meta_command(command)
        else:
            self.logger.error('The command type \"{}\" is unknown.'.format(command_type))

        self.acknowledge_action_complete()

    def process_robot_command(self, command):
        if not self.init_robot:
            self.logger.error('Called a robot command, but the robot it not initiated.')
            raise robcon.RobotInitError('Called a robot command, but the robot it not initiated.')

        regex_obj = re.match(r'([\D]*)(\d+(?:\.\d+)?)?', command)
        command = regex_obj.group(1)
        param = regex_obj.group(2)
        self.logger.info('Detected the robot command \"{}\" with the following parameters: {}'.format(command, param))

        if command == robcmd.START:
            self.rob.start_robot()
        elif command == robcmd.RANDMOVE:
            self.rob.move_robot_randomly()
        elif command == robcmd.STRAIGHTMOVE:
            distance = float(param)
            self.rob.move_robot_straight(distance)
        elif command == robcmd.STRAIGHTMOVE_BACKWARDS:
            distance = float(param)
            self.rob.move_robot_straight(distance, backwards=True)
        elif command == robcmd.SPIN:
            angle = int(param)
            self.rob.spin_robot(angle)
        elif command == robcmd.SPIN_CLOCKWISE:
            angle = int(param)
            self.rob.spin_robot(angle, clockwise=True)
        elif command == robcmd.GLORIENTTES:
            self.rob.play_glorienttes_song()
        else:
            self.logger.error('The command \"{}\" is unknown.'.format(command))
            raise ValueError('The command \"{}\" is unknown.'.format(command))

    def process_meta_command(self, command):
        matches = [re.match(r'{}'.format(meta_command), command) for meta_command in robcmd.META_COMMANDS]
        matches = [match for match in matches if match is not None]
        spans = [match.span() for match in matches]
        match_lengths = [tup[1]-tup[0] for tup in spans]
        matched_command = matches[match_lengths.index(max(match_lengths))].group()

        if not matched_command:
            self.logger.error('The command \"{}\" is unknown.'.format(command))
            raise ValueError('The command \"{}\" is unknown.'.format(command))

        self.logger.info('Detected the meta command \"{}\".'.format(matched_command))

        if matched_command == robcmd.INIT_SESSION:
            # Get overwrite tag and path for the session folder
            regex_obj = re.search(r'o_([ft])_([\D\d]+)', command)
            overwrite = regex_obj.group(1)
            if overwrite == 't':
                overwrite = True
            elif overwrite == 'f':
                overwrite = False
            pathname = regex_obj.group(2)

            self.logger.info('\"{}\" has the following parameters: overwrite={}, '
                             'pathname={}'.format(matched_command, overwrite, pathname))

            self.init_session(pathname, overwrite)
        elif matched_command == robcmd.SET_MEASUREMENT_ID:
            pattern = r'({})_(\d+)'.format(robcmd.SET_MEASUREMENT_ID)
            regex_obj = re.search(pattern, command)

            measurement_id = int(regex_obj.group(2))
            self.sweep_controller.set_measurement_id(measurement_id)
        elif matched_command == robcmd.MEASURE:
            self.sweep_controller.conduct_measurement(playback=True)
        elif matched_command == robcmd.PLAYBACK_SWEEP:
            self.sweep_controller.play_sweep()
        elif matched_command == robcmd.START_RECORDING:
            self.sweep_controller.set_sweep_playback_complete(False)
            t_recording = threading.Thread(target=self.sweep_controller.record_until_stopped)
            t_recording.start()
            time.sleep(0.5)
        elif matched_command == robcmd.STOP_RECORDING:
            self.sweep_controller.set_sweep_playback_complete(True)
            self.sweep_controller.blockwiserecording2rirs()

    def init_session(self, session_name, overwrite):
        session_path = pathlib.Path('..', '..', 'measurements', session_name)
        session_path_str = str(session_path)
        try:
            session_path.mkdir(parents=True)

            self.logger.info('Creating the session directory \"{}\"'.format(session_path_str))

            self.sweep_controller.set_session_path(session_path_str)
        except FileExistsError:
            self.logger.warning('There is already a directory with the name \"{}\" on the '
                                'RaspberryPi'.format(session_path_str))

            # Maybe the directory exists already on the raspberry pi, therefore compare with the user's answer on
            # whether the directory shall be overwritten
            if overwrite:
                session_path.mkdir(exist_ok=True, parents=True)
                self.logger.warning('Overwriting the session directory \"{}\" on the '
                                    'RaspberryPi'.format(session_path_str))

                self.sweep_controller.set_session_path(session_path_str)
            else:
                self.logger.error('The user specified that no data shall be overwritten. Therefore, the script will '
                                  'exit now.')
                raise SystemExit('The user specified that no data shall be overwritten. Therefore, the script will '
                                 'exit now.')


class RobotClient(socket.socket):
    def __init__(self, raspberry_id=1, robot_type='', family=socket.AF_INET, socket_type=socket.SOCK_STREAM,
                 *args, **kwargs):
        super().__init__(family=family, type=socket_type, *args, **kwargs)

        self.logger = utils.init_logger('RobotClient')

        if raspberry_id == 1:
            self.address = (parameters.IP_RASPBERRY1, parameters.STANDARD_ROBOT_PORT)
        elif raspberry_id == 2:
            self.address = (parameters.IP_RASPBERRY2, parameters.STANDARD_ROBOT_PORT)
        else:
            raise SystemExit('RaspberryID must be either 1 or 2, but I got {}.'.format(raspberry_id))
        super().connect(self.address)

        if robot_type != parameters.ROBOT_TYPE_SOURCE and robot_type != parameters.ROBOT_TYPE_RECEIVER:
            raise SystemExit('Unknown sound device type: {}. Must be either \'{}\' or \'{}\'.'
                             .format(robot_type, parameters.ROBOT_TYPE_SOURCE, parameters.ROBOT_TYPE_RECEIVER))
        self.robot_type = robot_type

    def _send_command(self, command, command_type):
        command = '{}_{}'.format(command_type, command)
        command = command.encode('utf-8')

        self.sendall(command)
        self._wait_for_ack()

    def _wait_for_ack(self):
        while True:
            data = self.recv(1024)

            data = data.decode('utf-8')

            # waiting is finished as soon as server acknowledges that requested action is done
            if data == robcmd.ACK:
                break

    def init_session(self, session_name, overwrite=False):
        if overwrite:
            command_params = 'o_t_{}'.format(session_name)
        else:
            command_params = 'o_f_{}'.format(session_name)

        command = '{}_{}'.format(robcmd.INIT_SESSION, command_params)
        self._send_command(command, robcmd.TYPE_META)

    def set_measurement_id(self, id):
        command = '{}_{}'.format(robcmd.SET_MEASUREMENT_ID, id)
        self._send_command(command, robcmd.TYPE_META)

    def playback_sweep(self):
        if self.robot_type == parameters.ROBOT_TYPE_SOURCE:
            self._send_command(robcmd.PLAYBACK_SWEEP, robcmd.TYPE_META)
        else:
            self.logger.error('You have to call playback sweep on the source robot.')

    def start_recording(self):
        if self.robot_type == parameters.ROBOT_TYPE_RECEIVER:
            self._send_command(robcmd.START_RECORDING, robcmd.TYPE_META)
        else:
            self.logger.error('You have to call start recording on the receiver robot.')

    def stop_recording(self):
        if self.robot_type == parameters.ROBOT_TYPE_RECEIVER:
            self._send_command(robcmd.STOP_RECORDING, robcmd.TYPE_META)
        else:
            self.logger.error('You have to call stop recording on the receiver robot.')

    def init_robot(self):
        self._send_command(robcmd.START, robcmd.TYPE_ROBOT)

    def move_randomly(self):
        self._send_command(robcmd.RANDMOVE, robcmd.TYPE_ROBOT)

    def move_straight(self, distance):
        distance = float(round(distance, 2))
        if distance > 0:
            self._send_command(robcmd.STRAIGHTMOVE + str(distance), robcmd.TYPE_ROBOT)
        else:
            self._send_command(robcmd.STRAIGHTMOVE_BACKWARDS + str(abs(distance)), robcmd.TYPE_ROBOT)

    def spin(self, angle):
        angle = int(round(angle))
        if angle > 0:
            self._send_command(robcmd.SPIN + str(angle), robcmd.TYPE_ROBOT)
        else:
            self._send_command(robcmd.SPIN_CLOCKWISE + str(abs(angle)), robcmd.TYPE_ROBOT)

    def play_song(self):
        self._send_command(robcmd.GLORIENTTES, robcmd.TYPE_ROBOT)

    def measure(self):
        time.sleep(1)
        self._send_command(robcmd.MEASURE, robcmd.TYPE_ROBOT)
