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

def render(*commands):
    global render_buffer
    for command in commands:
        render_buffer += command

def renderCopy():
    global render_buffer
    sys.stdout.write(render_buffer)
    sys.stdout.flush()
    clearRenderBuffer()

def moveCursor(direction: str, amount=1):
    """
    direction:
      'A' - UP
      'B' - DOWN
      'C' - FORWARD
      'D' - BACK
    """
    amount = str(amount)
    render("\033["+amount+direction)

def screenClear():
    render("\033[2J")

class KeyboardInput:
    def __init__(self):
        self.pressed = 0
        self.key_mash_counter = 0

        if POSIX:
            tty.setraw(fd)

        # Control codes for POSIX/WINDOWS
        # UP DOWN RIGHT LEFT
            CONTROL_CODES = tuple(range(65,69))
        else:
            CONTROL_CODES = (72, 80, 77, 75)
        self.CONTROL_MAP = dict(zip(CONTROL_CODES, (CONTROLS.UP,
                                                    CONTROLS.DOWN,
                                                    CONTROLS.RIGHT,
                                                    CONTROLS.LEFT)))

    def _scan_in_control_codes(self, char):
        if char in self.CONTROL_MAP:
            return self.CONTROL_MAP[char]
        self.key_mash_counter += 1
        return KEY.QUIT if self.key_mash_counter > 5 else 0
        # Uncomment if you want to raise error for control codes that are not coded in yet
        # raise ValueError(f'Invalid control code: {char}')
        
    def keyIn(self):
        if POSIX:
            # Reads one chracter from input stream 
            char = ord(sys.stdin.read(1))
        else:
            # Gets keyboard input as UNICODE character
            # ord() converts to ascii
            key = msvcrt.getwch()
            char = ord(key)
# Test -             render('\033[1;1H')
# Test -             render(str(key))
# Test -         render('\033[2;1H' + str(char))

        # ASCII (a - ~)
        if 32 <= char <= 126:
            self.pressed = char
            self.key_mash_counter = 0
            return

        # Backspace
        elif char == 8:
# Test -             render("\033[3;5H Backspace")
            self.pressed = KEY.BACKSPACE
            self.key_mash_counter = 0
            return
        # Tab
        elif char == 9:
# Test -             render("\033[3;5H TAB")
            self.pressed = KEY.TAB
            self.key_mash_counter = 0
            return
        # ENTER
        elif char in {10, 13}:
# Test -             render("\033[3;5H ENTER")
            self.pressed = KEY.ENTER
            self.key_mash_counter = 0
            return
        # CTRL-C
        if char == 3:
            self.pressed = KEY.QUIT
            self.key_mash_counter = 0
            return

        if POSIX:
            if char == 27:
                # Control codes
                next1, next2 = ord(sys.stdin.read(1)), ord(sys.stdin.read(1))
                if next1 == 91:
# Test -                     render("\033[1;5H CONTROL")
                    self.pressed = self._scan_in_control_codes(next2)
                    if self.pressed != 0: self.key_mash_counter = 0
# Test -                     match self.pressed:
# Test -                         case CONTROLS.UP: 
# Test -                             render("^")
# Test -                         case CONTROLS.DOWN: 
# Test -                             render("v")
# Test -                         case CONTROLS.RIGHT: 
# Test -                             render(">")
# Test -                         case CONTROLS.LEFT: 
# Test -                             render("<")
# Test -                         case _:
# Test -                             render(str(char))
                    return

                # ESCAPE - If no control codes are inputted,
                #          ESC is being pressed
                self.pressed = CONTROLS.ESCAPE
                return

        # WINDOWS
        else:
            # Control codes
            if char == 0x00 or char == 0xE0:
                next_ = ord(msvcrt.getwch())
# Test -                 render("\033[2;5H CONTROL")
                self.pressed = self._scan_in_control_codes(next_)
                if self.pressed != 0: self.key_mash_counter = 0
# Test -                 match self.pressed:
# Test -                     case CONTROLS.UP: 
# Test -                         render("^")
# Test -                     case CONTROLS.DOWN: 
# Test -                         render("v")
# Test -                     case CONTROLS.RIGHT: 
# Test -                         render(">")
# Test -                     case CONTROLS.LEFT: 
# Test -                         render("<")
# Test -                     case _:
# Test -                         render(str(char))
                return

            elif char == 27: #ESC
# Test -                 render("\033[3;5H ESCAPE")
                self.pressed = CONTROLS.ESCAPE
                return

        self.pressed = 0

if __name__ == "__main__":
    try:
        init()
        
        keyboard = KeyboardInput()
        
        screenClear()
        for i in range(10000000):
            keyboard.keyIn()
            if keyboard.pressed == KEY.QUIT:
                break
            elif keyboard.pressed == CONTROLS.ESCAPE:
                 screenClear()
            render("\033[;H")
 
            renderCopy()

    finally:
        if POSIX:
            termios.tcsetattr(fd,termios.TCSADRAIN, old_settings)
    





