import vgamepad as vg
import time

class ETS2Interactor:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()

    def start_new_job(self):
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_START, sleep_after=0.2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, 8, sleep_after=0.2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, 3, sleep_after=0.2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=0.2, sleep_between=2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, 5, sleep_after=0.2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=0.2, sleep_between=2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, sleep_after=0.2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=0.2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, sleep_after=0.2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=0.2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, sleep_after=0.2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, 2, sleep_after=0.2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, 2, sleep_after=0.2, sleep_between=2)
        self.press_and_release_repeats(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, 5, sleep_after=0.2)
        self.press_and_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, sleep_after=0.2)


    def press_and_release_repeats(self, button, amount_of_presses, sleep_between=0, sleep_after=0):
        for i in range(amount_of_presses):
            self.press_and_release(button)
            self._sleep_if_needed(sleep_between)
        self._sleep_if_needed(sleep_after)

    def press_and_release(self, button, sleep_after=0):
        self.gamepad.press_button(button=button)
        self.gamepad.update()
        self.gamepad.release_button(button=button)
        self.gamepad.update()
        self._sleep_if_needed(sleep_after)

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
            self.gamepad.left_joystick_float(x_value_float=1, y_value_float=1)
            self.gamepad.update()
            print("wiggled to (1, 1)")
            time.sleep(0.1)

if __name__ == "__main__":
    interactor = ETS2Interactor()
    time.sleep(3)
    interactor.wiggle_joystick()
    # interactor.start_new_job()