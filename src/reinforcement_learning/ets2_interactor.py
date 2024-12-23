import vgamepad as vg
import time

class ETS2Interactor:
    def __init__(self, log_inputs=False):
        self.log_inputs = log_inputs
        self.gamepad = vg.VX360Gamepad()
        self.gamepad.reset()
        print("Starting virtual gamepad, you have 5 seconds to have the game focused")
        time.sleep(5)
        self.wiggle_joystick()
        self.reset_joysticks()
        print("Virtual gamepad ready")

    def start_new_job(self):
        menu_navigation_sleep_after = 1
        wait_time_for_menu_loading_long = 5
        wait_time_for_world_loading = 10
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_START, sleep_after=menu_navigation_sleep_after, sleep_between_press_and_release=0.5)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, 1, sleep_after=menu_navigation_sleep_after, sleep_between=menu_navigation_sleep_after)
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

    # Certain buttons won't be detected if they are relaesed immediately -> check if one of them is released immediately -> overwrite if true
    def correct_sleep_between_if_necesarry(self, button, sleep_between_press_and_release):
        if sleep_between_press_and_release == 0:
            if button == vg.XUSB_BUTTON.XUSB_GAMEPAD_START:
                print("Warning: anomaly detected, " + button.name + " will be released after 0.5 seconds instead of immediately")
                return 0.5
        return sleep_between_press_and_release

    def _sleep_if_needed(self, sleep_after):
        if sleep_after > 0:
            time.sleep(sleep_after)

    def wiggle_joystick(self):
        for i in range(10):
            self.gamepad.left_joystick_float(x_value_float=0.5, y_value_float=0.5)
            self.gamepad.update()
            print("wiggled to (0.5, 0.5)")
            self.gamepad.left_joystick_float(x_value_float=0, y_value_float=0)
            self.gamepad.update()
            print("wiggled to (0, 0)")
            self.gamepad.left_joystick_float(x_value_float=-0.5, y_value_float=-0.5)
            self.gamepad.update()
            print("wiggled to (-0.5, -0.5)")
            time.sleep(0.1)

    def reset_joysticks(self):
        self.gamepad.left_joystick(x_value=0, y_value=0)
        self.gamepad.right_joystick(x_value=0, y_value=0)
        self.gamepad.update()
        print("Reset gamepad joysticks")

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
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    
    def downshift(self):
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)

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
        interactor.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_START, sleep_between_press_and_release=0.1)
        print("finished, will be sleeping for a while")
        time.sleep(1000)

    def start_new_job(interactor: ETS2Interactor):
        print("Starting new job")
        interactor.start_new_job()

    def keep_gamepad_detected():
        print("keeping gamepad detected, nothing else will be done")
        time.sleep(1000) #simply keep gamepad detected


    interactor = ETS2Interactor(log_inputs=True)
    # keep_gamepad_detected()
    print("You have 10 seconds before code will continue")
    start_new_job(interactor)

