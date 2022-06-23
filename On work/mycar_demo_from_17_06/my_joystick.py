
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
            0x135 : 'R',
            0x137 : 'ZR',
            0x134 : 'L',
            0x136 : 'ZL',
            0x139 : 'Plus',
            0x138 : 'Minus',
            0x13c : 'Home',
            0x13d : 'Record',
            0x13b : 'Btn_Stick_Right',
            0x13a : 'Btn_Stick_Left',
        }


        self.axis_names = {
            0x1 : 'Vertical_Srick_Left',
            0x0 : 'Horizontal_Stick_Left',
            0x4 : 'Vertical_Stick_Right',
            0x3 : 'Horizontal_Stick_Right',
            0x11 : 'Vertical_Cross',
            0x10 : 'Horinzontal_Cross',
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
            'A' : self.toggle_mode,
            'Record' : self.erase_last_N_records,
            'Home' : self.emergency_stop,
            'Plus' : self.increase_max_throttle,
            'Minus' : self.decrease_max_throttle,
            'ZL' : self.toggle_constant_throttle,
            'ZR' : self.toggle_manual_recording,
        }


        self.axis_trigger_map = {
            'Horizontal_Stick_Left' : self.set_steering,
            'Vertical_Stick_Right' : self.set_throttle,
        }


