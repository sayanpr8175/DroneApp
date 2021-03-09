import logging, time, argparse, configparser, sys
import socket, os, signal, psutil

from subprocess import Popen
from drone import Drone 
from connection_watchdog import ConnectionWatchdog
from data_receiver import DataReceiver
from utils import Utils


parser = argparse.ArgumentParser()
parser.add_argument('--d', nargs=1, default=None)
args = parser.parse_args()

APP_DIR = args.d[0] if args.d != None else "./"
CONFIGURATIONS = APP_DIR + 'configuration.ini'

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(APP_DIR + 'logs/main app | ' + str(time.asctime()) + '.log'),
        logging.StreamHandler()
    ]
)


config = configparser.ConfigParser()

if len(config.read(CONFIGURATIONS)) == 0:
    logging.error("Could Not Read Configurations File: " + CONFIGURATIONS)
    sys.exit()

DRONE_ID = config['drone']['id']
HOST_IP = config['cloud-app']['ip'] 
DRONE_CLOUD_SERVER_PORT   = int( config['cloud-app']['control-port'])
MAX_RECONNECTION_ATTEMPTS = int( config['cloud-app']['max-reconnection-attempts'])

VIDEO_PORT = int(config['cloud-app']['video-port'])
GRAYSCALE = config['video']['grayscale'].lower() == 'true'
FRAMES_PER_SECOND = int(config['video']['fps'])
JPEG_QUALITY = int(config['video']['quality'])
WIDTH = int(config['video']['width'])
HEIGHT = int(config['video']['height'])




if __name__ == '__main__':
    logging.debug(" DroneApp has started!   Directory %s", APP_DIR)

    while(True):
        try:
            drone = Drone(config)
            break
        except Exception as e:
            logging.error(str(e), exc_info=True)
            time.sleep(2)


    watchdog = ConnectionWatchdog(drone, HOST_IP, MAX_RECONNECTION_ATTEMPTS)
    watchdog.start()

    video_streamer_proc = None
    control_server_socket = None 
    server_message_receiver = None

    while drone.is_active:
        try:
            while not watchdog.net_status:
                time.sleep(1)
            
            time.sleep(3)
            
            control_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control_server_socket.connect((HOST_IP, DRONE_CLOUD_SERVER_PORT))
            logging.info('Socket Connection Opened')

            droneIdBytes = Utils.createNetworkMessage(str.encode(DRONE_ID))
            control_server_socket.send(droneIdBytes)
            logging.info('Drone ID: %s Connected To Control Server Endpoint: %s:%s', str(DRONE_ID), HOST_IP, str(DRONE_CLOUD_SERVER_PORT))
    
            video_streamer_proc = Popen('/usr/bin/python3 ' + APP_DIR + 'video_streamer.py', shell=True)
            
            server_message_receiver = DataReceiver(control_server_socket, drone)
            server_message_receiver.start()
            
            while watchdog.net_status and drone.is_active:
                msg = Utils.createNetworkMessage(drone.getDroneDataSerialized())
                control_server_socket.send(msg)
                time.sleep(1)
            
        except Exception as e:
            logging.error(str(e), exc_info=True)
            drone.freeze()
            
        finally:
            if video_streamer_proc != None:
                current_process = psutil.Process(video_streamer_proc.pid)
                children = current_process.children(recursive=True)
                
                for child in children:
                    if child.pid != os.getpid():
                        os.kill(child.pid, signal.SIGKILL)

                os.kill(video_streamer_proc.pid, signal.SIGKILL)
            
            if control_server_socket != None:
                control_server_socket.close()
            if server_message_receiver != None:
                server_message_receiver.stop()
            

    drone.close()
    
    logging.info('Drone Offline')

    
    #logging.info('FPS: %s Quality: %s Width %s Height %s Grayscale: %s', str(FRAMES_PER_SECOND), str(JPEG_QUALITY), str(WIDTH), str(HEIGHT), GRAYSCALE)
    
    #logging.info('Drone ID: %s Video Recipient: %s:%s', str(DRONE_ID), str(HOST_IP), str(VIDEO_PORT))


##  To start a service on raspbian: 
##  sudo mv droneapp.service /lib/systemd/system/droneapp.service
##  sudo systemctl daemon-reload
##  sudo systemctl enable droneapp.service
##  sudo reboot

######## See the status of services
##     sudo systemctl status droneapp.service


#### To stop
##  sudo systemctl disable droneapp.service
##

### This service will start and die

### Run it for infinite loop









