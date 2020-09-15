import time

import robot_socket as robsock
import position_tracking as tracking

import measurement_utils as utils
import measurement_params as parameters

session_name, overwrite_flag = utils.initialize_session_env()

# Start logging server
logging_server = utils.start_logging_server()

logger = utils.init_logger('Main', add_logserver_handler=False)

# Initialize OpenVR for position tracking of robots
tracking_controller = tracking.PositionTracker()

# Wait for robot server to be started
input('Please go and start the RobotServer on both RaspberryPis now. After that you can continue by '
      'pressing any key.\n')

with robsock.RobotClient(raspberry_id=1, robot_type=parameters.ROBOT_TYPE_RECEIVER) as rcv_robot, \
        robsock.RobotClient(raspberry_id=2, robot_type=parameters.ROBOT_TYPE_SOURCE) as src_robot:

    rcv_robot.settimeout(120)
    src_robot.settimeout(120)

    # Init session on robots as well, i.e., create measurement folders etc.
    rcv_robot.init_session(session_name, overwrite_flag)
    src_robot.init_session(session_name, overwrite_flag)

    rcv_robot.init_robot()
    src_robot.init_robot()

    input('Please go and turn on the tracker on the receiver robot. After that you can continue by pressing any key.')
    tracking_controller.connect_tracker(parameters.ROBOT_TYPE_RECEIVER)
    input('Please go and turn on the tracker on the source robot. After that you can continue by pressing any key.')
    tracking_controller.connect_tracker(parameters.ROBOT_TYPE_SOURCE)
    time.sleep(5)

    metadata_frame = utils.init_metadata_frame()

    # Start measurement loop
    for measurement_id in range(1, parameters.MEASUREMENTS_PER_SESSION + 1):
        rcv_robot.set_measurement_id(measurement_id)
        src_robot.set_measurement_id(measurement_id)

        time_obj = utils.get_current_localtime_obj()

        position_rcv, position_src = tracking_controller.measure_positions(parameters.TRACKING_N_AVERAGES)
        logger.info('Receiver is currently located at {} and has the orientation {}.'.format(position_rcv.position,
                                                                                             position_rcv.orientation))
        logger.info('Source is currently located at {} and has the orientation {}.'.format(position_src.position,
                                                                                           position_src.orientation))

        metadata_frame = utils.add_measurement_to_frame(metadata_frame, measurement_id, time_obj,
                                                        position_rcv, position_src)

        # Save metadata
        utils.save_metadata(metadata_frame, session_name)

        rcv_robot.start_recording()
        src_robot.playback_sweep()
        rcv_robot.stop_recording()

        # Move to next positions
        rcv_robot.move_randomly()
        src_robot.move_randomly()

        # wait for robots to stop shaking
        time.sleep(2)

logging_server.shutdown()
logging_server.server_close()
