# Change the working directory to the base directory
from os import chdir
from os import path as ospath 
from sys import path as syspath
chdir(ospath.expanduser("~/git/vaffelgutta"))
syspath.append(ospath.abspath(ospath.expanduser("~/git/vaffelgutta")))

from camera.runaruco import camera_launch  # Import the external ArUco pose estimation module
from camera.runaruco import camera_close  # It seems you might need this method to close the process
from robot_workspace.assets.Wafflebot import Wafflebot
from robot_workspace.assets import arm_positions
from robot_workspace.backend_controllers import safety_functions as safety 
from time import sleep
import numpy as numphy

def main():

    camera_launch()
    bot = Wafflebot()
    bot.arm.go_to_home_pose()
    sleep(120)
    bot.safe_stop()
    camera_close()
    
# Footer:
def handle_error(signum, frame):raise KeyboardInterrupt
if __name__ == '__main__':
    from signal import signal, SIGINT; signal(SIGINT, handle_error)
    try:
        main()
    # if error detected, run the error handler
    except (KeyboardInterrupt, Exception) as error_program_closed_message:
        with open("robot_workspace/backend_controllers/errorhandling.py") as errorhandler: exec(errorhandler.read())
    
