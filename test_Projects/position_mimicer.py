# Change the working directory to the base directory
from os import chdir, getcwd
from os import path as ospath 
from sys import path as syspath
chdir(ospath.expanduser("~/git/vaffelgutta"))
syspath.append(ospath.abspath(ospath.expanduser("~/git/vaffelgutta")))

# interbotix modules
from interbotix_common_modules.common_robot.robot import robot_startup, robot_shutdown
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
# user libraries: 
from robot_workspace.backend_controllers import robot_boot_manager
from time import sleep

def main():
    robot_boot_manager.robot_launch(use_real_robot=False)
    bot = InterbotixManipulatorXS(robot_model="vx300s",
                                  group_name="arm",
                                  gripper_name="gripper",
                                  accel_time=0.05)
    
    robot_startup()
    bot.arm.go_to_home_pose()
    bot.arm.go_to_sleep_pose()
    sleep(2)
    bot.core.robot_torque_enable("group", "arm", False)
    sleep(5)
    bot.core.robot_torque_enable("group", "arm", True)
    bot.arm.capture_joint_positions()
    savedpose = bot.arm.get_ee_pose() 
    print(savedpose)
    sleep(5)
    bot.arm.go_to_home_pose()
    bot.arm.set_ee_pose_matrix(savedpose)
 
    bot.arm.go_to_home_pose()
    bot.arm.go_to_sleep_pose()
    sleep(1)

    robot_shutdown()
    robot_boot_manager.robot_close()



if __name__ == '__main__':    
    try:
        main()
    # if error detected, run the error handler
    except (KeyboardInterrupt, Exception) as error_program_closed_message:
        print(getcwd)
        with open("robot_workspace/backend_controllers/errorhandling.py") as errorhandler: exec(errorhandler.read())
