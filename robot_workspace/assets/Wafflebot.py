# Change the working directory to the base directory
from os import chdir
from os import path as ospath 
from sys import path as syspath
chdir(ospath.expanduser("~/git/vaffelgutta"))
syspath.append(ospath.abspath(ospath.expanduser("~/git/vaffelgutta")))

from interbotix_common_modules.common_robot.robot import robot_startup, robot_shutdown
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
from interbotix_common_modules.angle_manipulation import angle_manipulation


from robot_workspace.assets import arm_joint_states, arm_positions, arm_offsets
from robot_workspace.backend_controllers import robot_boot_manager
from robot_workspace.backend_controllers.tf_publisher import publish_tf
from robot_workspace.backend_controllers import safety_functions

from time import sleep
import argparse
import threading
import numpy as numphy
from importlib import reload as import_reload

from sys import modules as sysmodules
if "Jetson.GPIO" in sysmodules: # Check if running on Jetson
    import Jetson.GPIO as GPIO


def calculate_translation(startpos: list, endpos: list):
    """Calculate the translation of two 4x4 matrices"""
    x = endpos[0][3] - startpos[0][3]
    y = endpos[1][3] - startpos[1][3]
    z = endpos[2][3] - startpos[2][3]
    return (x, y, z)
    

class Wafflebot:
    #Todo: Replace bota.arm.go_to_home_pose og ....sleep_pose with error checked versions. 
    def __init__(self, use_real_robot = False):
        # Include launch arguments 
        parser = argparse.ArgumentParser(description="Runs a wafflebot")
        parser.add_argument("-r", required=False, type=int, default=0, help="1 to use real robot, 0 to simulate")
        args = parser.parse_args()
        self.use_real_robot = bool(args.r)

        if use_real_robot == True: self.use_real_robot = True # Override launch option if program specifies real bot

        robot_boot_manager.robot_launch(use_real_robot=self.use_real_robot)
        self.bot = InterbotixManipulatorXS(
            robot_model= "vx300s",
            group_name="arm",
            gripper_name="gripper",
            )
        
        # Define shorthands to call bot functions intuitively 
        self.arm = self.bot.arm
        self.gripper = self.bot.gripper
        self.core = self.bot.core

        # start up robot
        self.arm.capture_joint_positions()
        robot_startup()
        self.arm.capture_joint_positions()
        
        # Monitor emergency stop
        if "Jetson.GPIO" in sysmodules: # Check if running on Jetson
            # **Start GPIO monitoring in a separate thread**
            self.gpio_thread = threading.Thread(
                target=self.monitor_gpio,
                daemon=True
                  )
            self.gpio_thread.start()
    
    # return the methods of the child class
    def __getattr__(self, name):
        return getattr(self.bot, name)
    
    
    def exit(self):
        robot_shutdown()  
        robot_boot_manager.robot_close()
    
    
    def safe_stop(self, slow = False):
        self.arm.set_trajectory_time(moving_time=(8.0 if slow else 2.0)) # reset moving time if changed elsewhere
        self.bot.core.robot_torque_enable("group", "arm", True)
        sleep(2)
        self.arm.go_to_home_pose()
        self.arm.go_to_sleep_pose()
        sleep(0.5)
        self.exit()


    def monitor_gpio(self):
        """ Function to monitor GPIO button in a separate thread. """
        # Set the GPIO mode
        GPIO.setmode(GPIO.BOARD)
        button_pin = 18  # Define button pin
        # Set the pin as an input
        GPIO.setup(button_pin, GPIO.IN)#punll_up_down=GPIO.PUD_DOWN)
              
        while True:
            pin_state = GPIO.input(button_pin)
            if pin_state == GPIO.LOW:
                self.safe_stop(slow = True)
                break
            sleep(0.1)  # Prevent CPU overuse
    
    
    def cancel_movement(self):
        current_pose = self.arm.get_ee_pose()
        self.arm.set_ee_pose_matrix(current_pose)
    

    def big_movement(self, joint_state_target: str, target_position_matrix = None):
        """
        moves the bot to a faraway place. requires a preset waypoint in joint space
        A list of joint states are stored in assets/arm_joint_states.py
        :input: joint_state_target: The joint state to go to
        :input: target_position_matrix: optional parameter to adjust waist position to point towards the given direction  
        """
        
        import_reload(arm_joint_states)
        joint_name = joint_state_target # save name for future use
        joint_state_target = getattr(arm_joint_states,joint_name)
        
        # If a target matrix is given, adjust the joint first  
        if target_position_matrix != None:
            
            # To ensure compatibility - cast to a numphy matrix
            target_position_matrix = numphy.matrix(target_position_matrix)             
            # extract the angle of the position
            target_x = target_position_matrix[3,0]
            target_y = target_position_matrix[3,1]
            target_rad = numphy.atan2(target_y, target_x)
            # commit the position    
            joint_state_target[0] = target_rad
        
        # Check the feasability of the movement 
        joint_state_target = safety_functions.fix_joint_limits(joint_state_target)
        # If an error was raised, abort movement
        if joint_state_target[0] == False: 
            print("big_movement: joint positions not reachable - aborting movement")
        # Else, move.
        else:
            self.arm.set_joint_positions(joint_state_target)
            self.small_movement(joint_name)
    
    def small_movement(self, target_matrix:str):
        import_reload(arm_positions)
        target_matrix = getattr(arm_positions,target_matrix)
        self.arm.capture_joint_positions() # in hopes of reminding the bot not to kill itself with its next move
        waypoints = safety_functions.check_collisions(
                bot=self.bot,
                start_pose_matrix = self.arm.get_ee_pose(),
                end_pose_matrix= target_matrix
                )
        


        for waypoint in waypoints:
            joints = self.arm.get_joint_positions()
            
            
            joints = self.arm.set_ee_pose_matrix(
                waypoint,
                execute=False,
                custom_guess=joints
                )[0]            
            joints = safety_functions.fix_joint_limits(joints=joints)

            ####
            #Todo: precalculate this or skip it outright
            #self.arm.set_single_joint_position("waist",joints[0],blocking=False)
            ###       
            if joints[0] == False:
                print("small_movement failed.")
                return
                #todo error handling

            
            # if joint values are "out of wack", retry with upright-er positions 
            for i in range(1,6):
                if abs(joints[i]) > numphy.pi/2:
                    joints[i] = 0.0
            
            joints = self.arm.set_ee_pose_matrix(
                waypoint,
                execute=False,
                custom_guess=joints
                )[0]
            joints = safety_functions.fix_joint_limits(joints=joints)            

        
            if joints[0] == False:
                print("Small_movement failed.")
                return
                #todo error handling
        
            self.arm.set_joint_positions(joints)
        return
    
    def go_to(self, position_name: str):
        #todo big movement if approporiate
        self.small_movement(position_name)