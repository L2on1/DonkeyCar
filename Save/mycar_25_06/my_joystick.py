
from donkeycar.parts.controller import Joystick, JoystickController


class MyJoystick(Joystick):
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

            
        self.button_names = {
            0x131 : 'A',
            0x130 : 'B',
            0x132 : 'Y',
            0x133 : 'X',
            0x13c : 'home',
            0x13d : 'record',
            0x139 : 'plus',
            0x138 : 'minus',
            0x135 : 'R',
            0x137 : 'ZR',
            0x134 : 'L',
            0x136 : 'ZL',
        }


        self.axis_names = {
            0x4 : 'joy_Y_right',
            0x3 : 'joy_X_right',
            0x0 : 'joy_X_left',
        }



class MyJoystickController(JoystickController):
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        #attempt to init joystick
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        #init set of mapping from buttons to function calls
            
        self.button_down_trigger_map = {
            'X' : self.toggle_mode,
            'record' : self.erase_last_N_records,
            'Y' : self.emergency_stop,
            'plus' : self.increase_max_throttle,
            'minus' : self.decrease_max_throttle,
            'R' : self.toggle_constant_throttle,
            'L' : self.toggle_manual_recording,
        }


        self.axis_trigger_map = {
            'joy_X_left' : self.set_steering,
            'joy_Y_right' : self.set_throttle,
        }


