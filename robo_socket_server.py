import argparse

import robot_socket as robosock
import measurement_params as parameters

parser = argparse.ArgumentParser(description='Starts a robot server on the specified RaspberryPi.')
parser.add_argument('raspberry_idx', metavar='i', type=int, nargs='?',
                    help='An index that specifies which RaspberryPi runs this script')
args = parser.parse_args()

if args.raspberry_idx == 1:
    server_address = parameters.IP_RASPBERRY1
elif args.raspberry_idx == 2:
    server_address = parameters.IP_RASPBERRY2
else:
    raise SystemExit('RaspberryIdx must be either 1 or 2, but I got {}.'.format(args.raspberry_idx))

with robosock.RobotServer() as rs:
    connection = rs.wait_for_connection(host_address=server_address)
    connection.start_receiver_loop()
