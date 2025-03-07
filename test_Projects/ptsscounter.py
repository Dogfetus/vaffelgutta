# Change the working directory to the base directory
from os import chdir
from os import path as ospath 
from sys import path as syspath
chdir(ospath.expanduser("/home/vaffel/git/vaffelgutta"))
syspath.append(ospath.abspath(ospath.expanduser("/home/vaffel/git/vaffelgutta")))
from sys import modules as sysmodules
from time import sleep
from importlib import reload as import_reload
if not "Jetson.GPIO" in sysmodules: # Check if running on Jetson
    import Jetson.GPIO as GPIO
else:
    print("Please run on a jetson nano device.")

def read_counter():     
    with open("test_Projects/ptscount.txt", "r") as file:
        count = file.read()
    return int(count)

def write_counter(count: int):
    with open("test_Projects/ptscount.txt", "w") as file:
        file.write(str(count))
    return

def main():
    #init counter 
    try:
        count = read_counter()
    except FileNotFoundError:
        write_counter(1)
    # Set the GPIO mode
    GPIO.setmode(GPIO.BOARD)
    button_pin = 18  # Define button pin
    # Set the pin as an input
    GPIO.setup(button_pin, GPIO.IN)
    
    #Read counter, increment if button pressed
    while True:
        pin_state = GPIO.input(button_pin)
        if pin_state == GPIO.LOW:
            count=read_counter()+1
            print(count)
            write_counter(count)
            sleep(3)
        sleep(0.1)  # Prevent CPU overuse


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
