# Code to be executed whenever an error is caused
from time import sleep
from interbotix_common_modules.common_robot.robot import robot_shutdown
from robot_workspace.backend_controllers import robot_boot_manager
try:
    bot.core.robot_torque_enable("group", "arm", True)
    print("\nRobot torquing successful!")
except NameError:
    print("\nrobot retorquing failed")
finally:
    if True:
        print("Error Caused. Shutting down robot.")
        # Countdown before stopping the robot - to create reaction time
        for i in range(0,11):
            try:
                sleep(1)
                print("Shutting down in: " + str(10-i) ) 
            
            # If pressed again, skip countdown and close immediately
            except KeyboardInterrupt:
                print("\nCtrl+c pressed again. Shutting down early:")
                break

        # Shut down robot using library
        try:
            robot_shutdown()
        except Exception as error_robot_shutdown_message:
            print("Error raised using robot_shutdown().\nError contents: " + str(error_robot_shutdown_message))
        finally:

        # shut down robot software
            try:
                robot_boot_manager.robot_close()
            except NameError:
                print("Error: Program closed without valid PID")
            # Catch keyboard interrupt special case:
            if repr(error_program_closed_message) == "KeyboardInterrupt()":
                error_program_closed_message = "Ctrl+C (KeyboardInterrupt)"
            # Print error message  
            print("Program closed by: " + str(error_program_closed_message))