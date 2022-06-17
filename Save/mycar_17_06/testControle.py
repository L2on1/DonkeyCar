from ctypes import sizeof
import os
import time
import logging

import donkeycar as dk
from donkeycar.parts.controller import JoystickController
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.throttle_filter import ThrottleFilter
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.lidar import RPLidar

import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def drive(cfg):

    logger.info(f'PID: {os.getpid()}')
    V = dk.vehicle.Vehicle()

    #Initialize logging before anything else to allow console logging
    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    if cfg.HAVE_MQTT_TELEMETRY:
        from donkeycar.parts.telemetry import MqttTelemetry
        tel = MqttTelemetry(cfg)


    if cfg.CONTROLLER_TYPE == "custom":  #custom controller created with `donkey createjs` command
        from my_joystick import MyJoystickController
        ctr = MyJoystickController(
        throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
        steering_scale=cfg.JOYSTICK_STEERING_SCALE,
        auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE)
        ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
        
    elif cfg.CONTROLLER_TYPE == "xbox": # Config manette xbox
        from donkeycar.parts.controller import XboxOneJoystickController
        ctr = XboxOneJoystickController(0.01) # Taux de rafraîchissement à 100 Hz ici
        
    else:
        print("Pas de manette configurée !\n")
    
    # Ajoute la manette
    V.add(
            ctr, 
            inputs=[], 
            outputs=['angle', 'throttle'],
            threaded=True)
    

    
########################################## Config Moteurs + servo-moteur #########################################
    steering_controller = PCA9685(cfg.STEERING_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
    steering = PWMSteering(controller=steering_controller,
                                    left_pulse=cfg.STEERING_LEFT_PWM,
                                    right_pulse=cfg.STEERING_RIGHT_PWM)

    throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
    throttle = PWMThrottle(controller=throttle_controller,
                                    max_pulse=cfg.THROTTLE_FORWARD_PWM,
                                    zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                                    min_pulse=cfg.THROTTLE_REVERSE_PWM)

    V.add(steering, inputs=['angle'], threaded=True)
    V.add(throttle, inputs=['throttle'], threaded=True)
    
###################################################################################################################



    
    cam = PiCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE, vflip=cfg.CAMERA_VFLIP, hflip=cfg.CAMERA_HFLIP)
    V.add(cam, outputs=['cam/image_array'])


    # LIDAR: ne fonctionne pas (lidar qu'on est incompatible ?)
    # Erreur: File "/home/pi/env/lib/python3.7/site-packages/rplidar.py", line 189, in _read_descriptor
    #        raise RPLidarException('Incorrect descriptor starting bytes')
    #        rplidar.RPLidarException: Incorrect descriptor starting bytes
    #
    # if cfg.LIDAR_TYPE == 'RP':
    #     print("adding RP lidar part")
    #     lidar = RPLidar(lower_limit = cfg.LIDAR_LOWER_LIMIT, upper_limit = cfg.LIDAR_UPPER_LIMIT)
    #     V.add(lidar, inputs=[],outputs=['lidar/dist_array'], threaded=True)
    # if cfg.LIDAR_TYPE == 'YD':
    #     print("YD Lidar not yet supported")



    if isinstance(ctr, JoystickController): # Affiche config manette
            print("You can now move your joystick to drive your car.")
            #ctr.set_tub(tub_writer.tub)
            ctr.print_controls()




    class DebugControll(): # Classe de deboguage
        
        def run(self, angle, throttle):
            print("Angle: ", angle)
            print("Throttle", throttle)
            return
    #V.add(DebugControll(), inputs=['angle', 'throttle'])


    class DebugCamera():
        
        def run(self, img):
            print(img.shape)
            return
    #V.add(DebugCamera(), inputs=['cam/image_array'])

    class DebugLIDAR():

        def run(self, lid):
            print(lid.shape)
            return
    #V.add(DebugLIDAR(), inputs=['lidar/dist_array'])






    

    #this throttle filter will allow one tap back for esc reverse
    th_filter = ThrottleFilter()
    V.add(th_filter, inputs=['throttle'], outputs=['throttle'])

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ, max_loop_count=cfg.MAX_LOOPS)



if __name__ == '__main__':
    cfg = dk.load_config(myconfig="myconfig.py")

    drive(cfg)
