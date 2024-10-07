import sys, os
import KEY, CONTROLS

if os.name == "posix":
    import tty, termios
    POSIX = True
    WINDOWS = False
else:
    import msvcrt
    WINDOWS = True
    POSIX = False

render_buffer = ""

def init():
    global render_buffer

    # Posix systems  - i.e mac/linux
    if POSIX:
        global fd, old_settings
        fd = sys.stdin.fileno()
        old_settings =  termios.tcgetattr(fd)

    render_buffer = ""

def clearRenderBuffer():
    global render_buffer
    render_buffer = ""

def render(command):
    global render_buffer
    render_buffer += command

def renderCopy():
    global render_buffer
    sys.stdout.write(render_buffer)
    sys.stdout.flush()
    clearRenderBuffer()

def moveCursor(direction: str, amount=1):
    amount = str(amount)
    render("\033["+amount+direction)

def screenClear():
    render("\033[2J")

class KeyboardInput:
    def __init__(self):
        self.pressed = -1

        if POSIX:
            tty.setraw(fd)

        # Control codes for POSIX/WINDOWS
        # UP DOWN RIGHT LEFT
            self.CONTROL_CODES = range(65,69)
        else:
            self.CONTROL_CODES = (72, 80, 77, 75)

    def _scan_in_control_codes(self, char):
        match char:
            case self.CONTROL_CODES[0]: # UP
                self.pressed = CONTROLS.UP
                return
            case self.CONTROL_CODES[1]: # DOWN
                self.pressed = CONTROLS.DOWN
                return
            case self.CONTROL_CODES[2]: # RIGHT
                self.pressed = CONTROLS.RIGHT
                return
            case self.CONTROL_CODES[3]: # LEFT
                self.pressed = CONTROLS.LEFT
                return
            case _:
                return None

        
    def keyIn(self):
        if not msvcrt.kbhit():
            return

        if POSIX:
            # Reads one chracter from input stream 
            char = ord(sys.stdin.read(1))
        else:
            # Gets keyboard input as UNICODE character
            # ord() converts to ascii
            key = msvcrt.getwch()
            char = ord(key)
            render(str(key) + '\n' + str(char))

        # ASCII a - ~
        if 32 <= char <= 126:
            self.pressed = char
            return

        if WINDOWS:
            if char == 0x00 or char == 0xE0:
                next_ = ord(msvcrt.getwch())
                _scan_in_control_codes(next_)

            elif char == 27: #ESC
                self.pressed = KEY.ESC

        elif POSIX:
            if char == 3: # CTRL-C
                self.pressed = KEY.QUIT
                return
               return
            elif char in {10, 13}:
                self.pressed = KEY.ENTER
                return
            elif char == 27:
                next1, next2 = ord(sys.stdin.read(1)), ord(sys.stdin.read(1))
                if next1 == 91:
                    _scan_in_control_codes(next2)
        self.pressed = -1

if __name__ == "__main__":
    keyboard = KeyboardInput()

    screenClear()
    for i in range(10000000):
        keyboard.keyIn()
        if keyboard.pressed == KEY.QUIT:
            break
        elif keyboard.pressed == KEY.ESC:
             screenClear()

        render("\033[;H")
        renderCopy()





