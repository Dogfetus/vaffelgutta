# Change the working directory to the base directory
from os import chdir
from os import path as ospath 
from sys import path as syspath
chdir(ospath.expanduser("~/git/vaffelgutta"))
syspath.append(ospath.abspath(ospath.expanduser("~/git/vaffelgutta")))

from interbotix_common_modules.common_robot.robot import robot_startup, robot_shutdown
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
from interbotix_common_modules.angle_manipulation import angle_manipulation

from robot_workspace.backend_controllers import find_pose_from_matrix, robot_boot_manager
from robot_workspace.backend_controllers.tf_publisher import publish_tf
from robot_workspace.assets import check_safety
from time import sleep
import argparse

class Wafflebot:
    def __init__(self, use_real_robot = False):
        # Include launch arguments 
        parser = argparse.ArgumentParser(description="Runs a wafflebot")
        parser.add_argument("-r", required=False, type=int, default=0, help="1 to use real robot, 0 to simulate")
        args = parser.parse_args()
        self.use_real_robot = bool(args.r)

        if use_real_robot == True: self.use_real_robot = True # Override launch option if program specifies otherwise

        robot_boot_manager.robot_launch(use_real_robot=self.use_real_robot)
        self.bot = InterbotixManipulatorXS(
            robot_model= "vx300s",
            group_name="arm",
            gripper_name="gripper",
            )
        
        self.arm = self.bot.arm
        self.gripper = self.bot.gripper
        self.core = self.bot.core
        self.arm.capture_joint_positions()
        robot_startup()
        self.arm.capture_joint_positions()

    def __getattr__(self, name):
        return getattr(self.bot, name)
    
    def exit(self):
        robot_shutdown()
        robot_boot_manager.robot_close()
    
    def cancel_movement(self):
        current_pose = self.arm.get_ee_pose()
        self.arm.set_ee_pose_matrix(current_pose)
    
    def safe_stop(self):
        self.bot.core.robot_torque_enable("group", "arm", True)
        sleep(2)
        self.arm.go_to_home_pose()
        self.arm.go_to_sleep_pose()
        sleep(0.5)
        self.exit()

    def go_to(self, target):
        self.arm.capture_joint_positions() # in hopes of reminding the bot not to kill itself with its next move
        publish_tf(target)
        target_matrix = find_pose_from_matrix.compute_relative_pose(target, self.arm.get_ee_pose())
        target_matrix = check_safety.check_safety(self.bot, target_matrix)
        if target_matrix[3][0] == 1: return False # if safety bit is 1, cancel movement 
        goal_pose = find_pose_from_matrix.find_pose_from_matrix(target_matrix)
        sleep(1)
        print("coo")
        publish_tf(angle_manipulation.pose_to_transformation_matrix(goal_pose)) 
        print("car")
        if not (self.arm.set_ee_cartesian_trajectory(goal_pose)):
            self.arm.set_ee_pose_matrix(target)
        self.arm.capture_joint_positions() # in hopes of reminding the bot not to kill itself with its next move
        return