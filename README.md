Usually, the following procedure has to be followed:
0. Adapt all parameters in measurement_params.py to your setup, especially IP addresses around
device names are crucial for the script to work properly. Place robots in middle of the room,
directly facing each other and as close as possible
1. Turn on the Roomba iCreate 2 robots, microphone array and loudspeaker. Connect
the Raspberry Pis to power.
2. Execute robo_socket_client.py on your measurement laptop.
3. Execute robo_socket_server.py on the Raspberry Pis and provide as an argument either
1 or 2 to tell the script which robot is receiver or source respectively.
4. Turn on one Vive Tracker after another.

Most of these steps will also appear as prompts on your measurement laptop after
executing robo_socket_client.py.


Additional hints:
- HTC Vive base stations outside play area
- Facing approx 45 downwards
- Room Calibration
  - Make sure that HTC Vive headset is inside the play area
  - Use advanced mode to put points manually and have straight edges
  - Go around the base stations with the controllers and look if the controller position coincides with the base station position on the computer screen if you have them at the same location, otherwise something is wrong with the base station placement or the previous steps
  - Ensure that the form you marked is somewhat close to your play area, otherwise do the previous steps again or move base stations a little.
  - Make a screen shot of the calibration window with the corner points of the play area
- Make sure that all devices are placed correctly on the robot
- Microphone should have the Zoom logo at the front of the robot (i.e. towards forward driving direction)
- Trackers should have status led at back of the robot (i.e.towards backward driving direction)
- Power banks should be attached at the front of the robot, because they are good for stability
- Connect all devices with the Raspberry Pis
- Turn on Microphone array and put it into I/O Mode with Ambisonics (e.g. B-Format, FuMa) settings, write down which convention you picked
- Set the gain of the microphone array to 1
- Use the low voltage loudspeaker input (i.e. the lower one when the membrane is pointing upwards)
- Make sure all IP addresses in the scripts are correct
- Run ifconfig -a on the Pis or ipconfig -all on a Mac measurement laptop to find out
- Set the max straight drive times according to room dimensions
- Adapt sweep length according to room
- Set max RIR length according to room
- Set the amount of desired measurements
- Turn on the HTC Vive connector box
- Measure room corners with the trackers mounted on the robots, this is crucial for determining the coordinate system later
  - Measure positions that would span your x and y axis
  - Measure orientation angles of robots
- Place robots in middle of the room, directly facing each other and as close as possible
- Turn on robots by pressing the button
- Light should be green, usually it says “English”


Guide on installing RaspberryPi:
- Prepare MicroSD card with Raspberry Pi Imager. Just use standard RapsberryPi OS
- Plug all cables (usb keyboard and mouse, HDMI) to Pi and then the power cable
- Carefully go through setup
- It will take 2-3 times until all updates are done
- For me, there were both times errors, requiring me to additionally run sudo dpkg --configure -a
- Go to RaspberryPi Configuration and change the hostname from raspberrypi to pi
- To enable connecting via ssh and Remote Desktop:
  - Enable SSH and VNC in configuration
    sudo apt install tightvncserver -y
    sudo apt --fix-broken install
    sudo apt install xrdp -y
- Set up Code and measurement folder from git
- python3 -m pip install -r requirements.txt
- sudo apt-get install python-dev libatlas-base-dev
- sudo apt-get install libasound-dev
- sudo apt-get install libportaudio2
