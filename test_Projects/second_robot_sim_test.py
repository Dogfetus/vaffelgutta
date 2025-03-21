import robot_boot_manager
from time import sleep

from interbotix_common_modules.common_robot.robot import robot_shutdown, robot_startup
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS


def main():
    pid = robot_boot_manager.robot_launch(use_real_robot=False)
    
    bot = InterbotixManipulatorXS(
        robot_model='vx300s',
        group_name='arm',
        gripper_name='gripper',
        accel_time=0.05
    )

    robot_startup()

    bot.arm.go_to_home_pose()
    bot.arm.set_single_joint_position("shoulder", 0.5)
    saved_position = bot.arm.get_ee_pose()
    print(saved_position)
    bot.arm.go_to_home_pose()
    bot.gripper.release()
    bot.arm.set_ee_pose_components(x = 0.30, y=-0.20, z=0.20, roll=0, pitch=0, yaw=0)
    bot.gripper.grasp()
    #print("\n")
    #print(bot.arm.get_joint_commands())
    sleep(0.3)
    bot.arm.set_ee_pose_matrix(saved_position)
    bot.gripper.release()
    sleep(0.5)
    bot.arm.go_to_sleep_pose()
    sleep(2)
    robot_shutdown()
    robot_boot_manager.robot_close()
    print("finished!")








# Footer:
def handle_error(signum, frame):raise KeyboardInterrupt
if __name__ == '__main__':
    from signal import signal, SIGINT; signal(SIGINT, handle_error)
    try:
        main()
    # if error detected, run the error handler
    except (KeyboardInterrupt, Exception) as error_program_closed_message:
        with open("robot/backend_controllers/errorhandling.py") as errorhandler: exec(errorhandler.read())
    
