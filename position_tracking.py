import openvr
import numpy as np
import time
import types

import measurement_params as params
import measurement_utils as utils


class PositionTrackingError(BaseException):
    pass


class PositionTracker:
    def __init__(self):
        self.logger = utils.get_logger('PositionTracker')

        try:
            openvr.init(openvr.VRApplication_Other)
        except openvr.error_code.InitError:
            self.logger.error('Could not init OpenVR. Please make sure that the Link box and HMD is connected and the '
                              'Link box is powered on.')
            raise
        self.logger.info('Successfully initialized OpenVR for the position tracking.')

        # get the VR System, that is an object to access all connected VR devices
        self.vr_system = openvr.VRSystem()

        self.tracker_idx_rcv = None
        self.tracker_idx_src = None

    def connect_tracker(self, tracker_type):
        if tracker_type != params.ROBOT_TYPE_RECEIVER and tracker_type != params.ROBOT_TYPE_SOURCE:
            self.logger.error('Tracker type must be either \'{}\' or \'{}\', but I got \'{}\'.'
                              .format(params.ROBOT_TYPE_SOURCE, params.ROBOT_TYPE_RECEIVER, tracker_type))
            raise PositionTrackingError('Tracker type must be either \'{}\' or \'{}\', but I got \'{}\'.'
                                        .format(params.ROBOT_TYPE_SOURCE, params.ROBOT_TYPE_RECEIVER,
                                                tracker_type))

        # get pose (i.e. status of all connected VR devices) to check which device is the tracker. Pose is an array,
        # where each device is represented by one entry
        pose = self.vr_system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                              openvr.k_unMaxTrackedDeviceCount)

        # Search for new active Trackers and write them to a list (ideally, this should only have one element, because
        # we can only add one tracker at a time to keep track of which one is source and receiver)
        n_active_trackers = 0
        active_index = []
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            # only append devices if they are connected
            if pose[i].bDeviceIsConnected:
                device_type = self.vr_system.getTrackedDeviceClass(i)

                # only append devices of type Tracker
                if device_type == openvr.TrackedDeviceClass_GenericTracker:
                    # only append trackers that are not connected yet
                    if i == self.tracker_idx_rcv or i == self.tracker_idx_src:
                        pass
                    else:
                        active_index.append(i)
                        n_active_trackers += 1

        if n_active_trackers == 0:
            self.logger.error('No new active tracking device. Please turn on a tracker in order to proceed.')
            raise PositionTrackingError('No tracking device active. Please turn on a tracker in order to proceed.')
        elif n_active_trackers > 1:
            self.logger.error('You can only add one tracker at a time, but there were {} new active '
                              'trackers. Please turn {} of them off again.'.format(n_active_trackers,
                                                                                   n_active_trackers-1))
            raise PositionTrackingError('You can only add one tracker at a time, but there were {} new active '
                                        'trackers. Please turn {} of them off again.'.format(n_active_trackers,
                                                                                             n_active_trackers-1))
        else:
            if tracker_type == params.ROBOT_TYPE_RECEIVER:
                self.tracker_idx_rcv = active_index[0]
            elif tracker_type == params.ROBOT_TYPE_SOURCE:
                self.tracker_idx_src = active_index[0]

    def measure_positions(self, n_averages=1):
        avg_position_rcv = orientation_rcv = avg_position_src = orientation_src = [0, 0, 0]
        for avg_idx in range(n_averages):
            pose = self.vr_system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                                  openvr.k_unMaxTrackedDeviceCount)

            position_rcv, orientation_rcv = self.pose_to_position(pose[self.tracker_idx_rcv].mDeviceToAbsoluteTracking)
            position_src, orientation_src = self.pose_to_position(pose[self.tracker_idx_src].mDeviceToAbsoluteTracking)

            avg_position_rcv += (1 / n_averages) * position_rcv
            avg_position_src += (1 / n_averages) * position_src

            time.sleep(1/params.TRACKING_FREQUENCY)

        position_rcv = types.SimpleNamespace()
        position_src = types.SimpleNamespace()

        position_rcv.position = avg_position_rcv
        position_rcv.orientation = orientation_rcv
        position_src.position = avg_position_src
        position_src.orientation = orientation_src
        return position_rcv, position_src

    @staticmethod
    def pose_to_position(pose):
        x = pose[0][3]
        y = pose[2][3]
        z = pose[1][3]

        yaw = 180 / np.pi * np.arctan2(pose[1][0], pose[0][0])
        pitch = 180 / np.pi * np.arctan2(pose[2][0], pose[0][0])
        roll = 180 / np.pi * np.arctan2(pose[2][1], pose[2][2])

        position = np.array([x, y, z])
        orientation = np.array([yaw, pitch, roll])
        return position, orientation

