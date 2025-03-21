from camera import Camera
from aruco import Aruco
from coordinatesystem import CoordinateSystem
from camera_config_loader import ConfigLoader                
        
def initalize_system():
    config_loader = ConfigLoader()
    camera = Camera(config_loader)
    aruco = Aruco()
    coord_sys = CoordinateSystem(config_loader)
    return camera, aruco, coord_sys

def main():
    camera, aruco, coord_sys = initalize_system()   

    while True:
        # Update pose estimation
        coord_sys.save_to_json(25)     
        
if __name__ == '__main__':
    main()