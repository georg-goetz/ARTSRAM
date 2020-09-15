import logging

DATA_DIR = '../Data/'

MEASUREMENTS_PER_SESSION = 300
MEASUREMENTS_PER_ARNI_COMBINATION = 20

INIT_ROBOT = True  # can be turned off for debugging purposes

SPEED_SPIN = 200  # Speed parameters. Suggested parameters: w/o carpet 150, carpet 200-250
SPEED_MOVE = 200  # Please keep move and turn parameters at the same speed.

MIN_RAND_SPIN_TIME = 0.5
MAX_RAND_SPIN_TIME = 4
MIN_RAND_DRIVE_TIME = 1
MAX_RAND_DRIVE_TIME = 15

# Set up all IP Addresses
IP_MAIN = '111.111.111.111'  # measurement laptop
IP_RASPBERRY1 = '111.111.111.111'  # raspberry 1, usually receiver
IP_RASPBERRY2 = '111.111.111.111'  # raspberry 2, usually source
STANDARD_ROBOT_PORT = 1234  # choose anything you want

# Set up sweep parameters
SWEEP_LENGTH = 10  # seconds
SWEEP_FS = 48000  # Hz

# Set up your sound devices. Use sounddevice.query_devices() to get a list of supported devices.
SD_IN_MAC = 'H3-VR'  # sound device name of microphone array (Mac workstation)
SD_OUT_MAC = 'Built-in Output'  # sound device name of loudspeaker (Mac workstation)
SD_IN_LINUX = 'H3-VR'  # sound device name of microphone array (Linux workstation)
SD_OUT_LINUX = 'bcm2835 ALSA: IEC958/HDMI (hw:0,1), ALSA'  # sound device name of loudspeaker (Linux workstation)

# Set up RIR parameters
MAX_RIR_LENGTH = 4  # in seconds, RIRs are cut to this length

# Tracking parameters
TRACKING_TIME_INTERVAL = 1  # currently not used
TRACKING_FREQUENCY = 250  # Hz
TRACKING_N_AVERAGES = 50  # position data is averaged over multiple returned values of HTC Vive

LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

ROBOT_TYPE_RECEIVER = 'RCV'
ROBOT_TYPE_SOURCE = 'SRC'
