import vgamepad as vg
import time
from reinforcment_learning.screen_grabber import ScreenGrabber
from reinforcment_learning.image_comparer import CursorOnDriveComparer
from reinforcment_learning.types import RequestedLightMode, CurrentLightMode
import threading
import random

class ETS2Interactor:
    def __init__(self, log_inputs=False, skip_initialize=False):
        self.log_inputs = log_inputs
        self.gamepad = vg.VX360Gamepad()
        self.screen_grabber = ScreenGrabber()
        self.cursor_on_drive_comparer = CursorOnDriveComparer()
        self._current_lights = CurrentLightMode.OFF
        self._high_beams_activated = False
        self.gamepad.reset()
        if not skip_initialize:
            print("Starting virtual gamepad, you have 10 seconds to have the game focused and the car in drive")
            time.sleep(10)
            self.wiggle_joystick(3)
            self.reset_joysticks()
            print("Virtual gamepad ready")
        else:
            print("skipped virtual gamepad initialisation")

    def start_new_job(self):
        print("Starting new job")
        self.reset_joysticks()
        menu_navigation_sleep_after = 1
        wait_time_for_menu_loading_long = 5
        wait_time_for_world_loading = 10
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_START, sleep_after=wait_time_for_menu_loading_long, sleep_between_press_and_release=0.1)
        if self.cursor_on_drive():
            self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, 1, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after)
        else: #cursor on system
            self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, 2, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, 3, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after) #move cursor to goto jobs
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after + wait_time_for_menu_loading_long) #select goto jobs, wait for it to load, select the first job
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, 5, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=menu_navigation_sleep_after + wait_time_for_menu_loading_long, sleep_between=menu_navigation_sleep_after + 2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, sleep_after=menu_navigation_sleep_after)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=menu_navigation_sleep_after + 2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, sleep_after=menu_navigation_sleep_after)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=menu_navigation_sleep_after + wait_time_for_menu_loading_long)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, sleep_after=menu_navigation_sleep_after)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, 3, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after + wait_time_for_menu_loading_long)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, 5, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=wait_time_for_world_loading)
        self.upshift()
        print("completed starting new job")

    def cursor_on_drive(self):
        return self.cursor_on_drive_comparer.compare_cursor_on_drive(self.screen_grabber.get_cursor_on_drive_image())

    def press_and_release_repeats(self, button, amount_of_presses, sleep_between=0, sleep_after=0):
        for i in range(amount_of_presses):
            self.press_and_release(button)
            if i < amount_of_presses - 1:
                self._sleep_if_needed(sleep_between)
        self._sleep_if_needed(sleep_after)

    def press_and_release(self, button, sleep_after=0, sleep_between_press_and_release=0):
        sleep_between_press_and_release = self.correct_sleep_between_if_necesarry(button, sleep_between_press_and_release)
        if self.log_inputs:
            print(f"Press and release {button.name}")
        self.gamepad.press_button(button=button)
        self.gamepad.update()
        self._sleep_if_needed(sleep_between_press_and_release)
        self.gamepad.release_button(button=button)
        self.gamepad.update()
        self._sleep_if_needed(sleep_after)


    def press_and_release_async(self, button, sleep_between_press_and_release=0.5):
        sleep_between_press_and_release = self.correct_sleep_between_if_necesarry(button, sleep_between_press_and_release)
        if self.log_inputs:
            print(f"Press and release {button.name}")
        self.gamepad.press_button(button=button)
        self.gamepad.update()
        threading.Thread(target=self._release_button_after_delay, args=(button, sleep_between_press_and_release), daemon=True).start()
        
    def _release_button_after_delay(self, button, sleep):
        time.sleep(sleep)
        self.gamepad.release_button(button=button)
        self.gamepad.update()
    
    # Certain buttons won't be detected if they are released immediately -> check if one of them is released immediately -> overwrite if true
    # No buttons will be detected if they are released immediately on slower machines
    def correct_sleep_between_if_necesarry(self, button, sleep_between_press_and_release):
        if sleep_between_press_and_release == 0:
            if button == vg.XUSB_BUTTON.XUSB_GAMEPAD_START:
                print("Warning: anomaly detected, " + button.name + " will be released after 0.5 seconds instead of immediately")
                return 0.5
            else:
                return 0.05
        return sleep_between_press_and_release

    def _sleep_if_needed(self, sleep_after):
        if sleep_after > 0:
            time.sleep(sleep_after)

    def wiggle_joystick(self, amount_of_wiggles=10):
        print("Starting wiggling left joystick")
        for i in range(amount_of_wiggles):
            self.gamepad.left_joystick_float(x_value_float=0.5, y_value_float=0.5)
            self.gamepad.update()
            self.gamepad.left_joystick_float(x_value_float=0, y_value_float=0)
            self.gamepad.update()
            self.gamepad.left_joystick_float(x_value_float=-0.5, y_value_float=-0.5)
            self.gamepad.update()
            time.sleep(0.1)
        print("Finished wiggling left joystick")

    def reset_joysticks(self):
        self.gamepad.left_joystick(x_value=0, y_value=0)
        self.gamepad.right_joystick(x_value=0, y_value=0)
        self.gamepad.update()

    def accelerate_full(self):
        self.update_brake_position(0)
        self.update_accelerater_position(1)
    
    def brake_full(self):
        self.update_brake_position(1)
        self.update_accelerater_position(0)
    
    def coast(self):
        self.update_brake_position(0)
        self.update_accelerater_position(0)

    def steer_left_full(self):
        self.update_steering_position(-1)

    def steer_right_full(self):
        self.update_steering_position(1)
    
    def steer_straight(self):
        self.update_steering_position(0)

    def indicate_left(self):
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
    
    def indicate_right(self):
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

    def update_accelerater_position(self, new_accelerater_position):
        self.gamepad.right_trigger_float(value_float=new_accelerater_position)
        self.gamepad.update()

    def update_brake_position(self, new_brake_position):
        self.gamepad.left_trigger_float(value_float=new_brake_position)
        self.gamepad.update()

    def update_steering_position(self, new_steering_position):
        self.gamepad.left_joystick_float(x_value_float=new_steering_position, y_value_float=0)
        self.gamepad.update()

    def upshift(self):
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER, sleep_between_press_and_release=0.05)
    
    def downshift(self):
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, sleep_between_press_and_release=0.05)
        
    #3 modes: off, parking, on. IF light control button is held for about 0.3 seconds, on will be transformed into high beams
    def update_lights(self, new_lights:RequestedLightMode):
        amount_of_switches = self._get_amount_of_light_toggles(new_lights, self._current_lights)
        if amount_of_switches > 0:
            self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_X, amount_of_switches, sleep_between=0.1)
        #check if need to update high beams
        if (new_lights == RequestedLightMode.HIGH_BEAMS and not self._high_beams_activated) or \
            (new_lights == RequestedLightMode.ON and self._high_beams_activated):
            self.press_and_release_async(vg.XUSB_BUTTON.XUSB_GAMEPAD_X, sleep_between_press_and_release=0.3)
            self._high_beams_activated = not self._high_beams_activated    
        self._update_current_lights_type(new_lights)       
        
        
    def _update_current_lights_type(self, new_lights:RequestedLightMode):
        match new_lights:
            case RequestedLightMode.OFF:
                self._current_lights = CurrentLightMode.OFF
            case RequestedLightMode.PARKING:
                self._current_lights = CurrentLightMode.PARKING
            case RequestedLightMode.ON | RequestedLightMode.HIGH_BEAMS:
                self._current_lights = CurrentLightMode.ON
        
    def _get_amount_of_light_toggles(self, new_lights:RequestedLightMode, current_lights:CurrentLightMode):
        match new_lights:
            case RequestedLightMode.OFF:
                match current_lights:   
                    case CurrentLightMode.OFF:
                        return 0
                    case CurrentLightMode.PARKING:
                        return 2
                    case CurrentLightMode.ON:
                        return 1
            case RequestedLightMode.PARKING:
                match current_lights:
                    case CurrentLightMode.OFF:
                        return 2
                    case CurrentLightMode.PARKING:
                        return 0
                    case CurrentLightMode.ON:
                        return 1
            case RequestedLightMode.ON | RequestedLightMode.HIGH_BEAMS:
                match current_lights:
                    case CurrentLightMode.OFF:
                        return 1
                    case CurrentLightMode.PARKING:
                        return 2
                    case CurrentLightMode.ON:
                        return 0
        return 0
        
    
    def turn_off_engine(self):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        self.gamepad.update()
        time.sleep(2)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        self.gamepad.update()
    
    def rest(self):
        #will only work when speed is zero
        self.turn_off_engine()
        self.press_A()

    def travel_via_ferry(self):
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=1, sleep_between=5)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, sleep_after=1)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=7)
    
    



if __name__ == "__main__":
    def trigger_button(interactor: ETS2Interactor):
        time.sleep(10)
        for i in range(0, 10):
            interactor.upshift()
            print("upshifted")
            time.sleep(1)
        print("finished, will be sleeping for a while")
        time.sleep(1000)

    def start_new_job(interactor: ETS2Interactor):
        print("Starting new job")
        interactor.start_new_job()

    def keep_gamepad_detected():
        print("keeping gamepad detected, nothing else will be done")
        time.sleep(1000) #simply keep gamepad detected
        
    def upshift(interactor:ETS2Interactor):
        time.sleep(5)
        print("upshift")
        interactor.upshift()
    
    def downshift(interactor:ETS2Interactor):
        time.sleep(5)
        print("downshift")
        interactor.downshift()
        time.sleep(5)
        print("downshift finished")
        interactor.downshift()
        
    def keep_gamepad_detected():
        interactor = ETS2Interactor(log_inputs=True, skip_initialize=True)
        interactor.reset_joysticks()
        # keep_gamepad_detected()
        
    def test_lighting_control():
        print("Running lighting control test")
        interactor = ETS2Interactor(log_inputs=True, skip_initialize=True)
        for i in range(30):
            choice = random.choice(list(RequestedLightMode))
            print("chose", choice)
            interactor.update_lights(choice)
            time.sleep(4)    

    test_lighting_control()
