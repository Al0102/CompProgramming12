import sys
from enum import Enum
from time import sleep
import operator
import KEY, CONTROLS
import tGame

"""
list<float> calculate(equation: list)
    returns calculated equation as list of ints
tuple<Error, int> calculate(equation: list)
    returns an tuple containing the error that occurred while parsing and the index where it occurs

void help_message(use_tGame_flag)
    displays help message
        parameters:
            input_
                input object (tGame.KeyboardInput), None for inpuT()
            use_tGame_flag
                displays using tGame.render() if set to True and print if false
"""

def main():
    input(
    """
    This program uses keyboard inputs and may take control
        of the terminal window/IO streams.
        Although it should return everything to normal upon
        program exit, there is a chance that I missed a bug
        somewhere so use at your own risk.

    Requires Python 3.10 or later

        [enter]

    """
    )
    accept_flag = 0
    for _ in range(20):
        confirm_open_calculator = input(
            "> I understand and wish to continue (y/n) "
            ).lower()
        match confirm_open_calculator:
            case 'n':
                break
            case 'y':
                accept_flag = 1
                break
    if not accept_flag:
        return 0

# Start Calcalexor
    try:
        tGame.init()
        key_input = tGame.KeyboardInput()

        tGame.render("\033]0;Calcalexor\x07")
        tGame.screenClear()
        tGame.renderCopy()

        if help_message(key_input, True) == KEY.QUIT:
            return

# Start main loop
        calcalexor = Calculator()
        exit_status = calcalexor.run_loop(key_input)

        tGame.screenClear()
        
        if exit_status != KEY.QUIT:
            tGame.render("\033[1;1H" + str(exit_status))
        
        tGame.renderCopy()

    finally:
        if tGame.POSIX:
            import tty, termios
            termios.tcsetattr(tGame.fd,termios.TCSADRAIN, tGame.old_settings)


class Calculator:
    ANS = '?'
    # A-Z + ANS
    VARIABLES = (
            *[chr(char) for char in range(KEY.K_A, KEY.K_Z+1)],
            ANS)
    # (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    NUMBERS = "0123456789"
    OPERATORS = "+-*/^"
    INPUT_MODES = Enum('INPUT_MODES', 'APPEND INSERT REPLACE')

    def __init__(self):
        self.history = []
        self.variables = {}
        for char in range(KEY.K_A, KEY.K_Z+1):
            self.variables[chr(char)] = 0
        self.variables[Calculator.ANS] = 0

        self._load_info()

        # equations vars
        self.input_mode = Calculator.INPUT_MODES.APPEND

    def __del__(self):
        self._save_info()

    def _load_info(self):
        try:
            with open ("data/variables.txt", 'r') as save_file:
                while var := save_file.readline():
                    var = var.split()
                    # self.variables[Variable name] = float(value.strip())
                    self.variables[var[0]] = float(var[1].strip())
        except FileNotFoundError:
            self._save_info(variables=True, history=False)


        try:
            # Newest to oldest equation 
            with open ("data/history.txt", 'r') as save_file:
                while var := save_file.readline():
                    self.history.append([x.strip() for x in var.split()])
        except FileNotFoundError:
            self._save_info(variables=True, history=False)
                
    def _save_info(self, variables=True, history=True):
        if variables:
            with open ("data/variables.txt", 'w') as save_file:
                for var, value in self.variables.items():
                    save_file.write(var+' '+str(value)+'\n')
    
        if history:
            # Newest to oldest equation 
            with open ("data/history.txt", 'w') as save_file:
                for equation in self.history:
                    save_file.write(' '.join(equation) + '\n')

    def reset_data(self, variables=True, history=True):
        if variables:
            self.variables = {}
            for char in range(KEY.K_A, KEY.K_Z+1):
                self.variables[chr(char)] = 0
            self.variables[Calculator.ANS] = 0
            self._save_info(variables=True, history=False)

        if history:
            self.history = []
            self._save_info(history=True, variables=False)

    def run_loop(self, key_input: tGame.KeyboardInput):
        query_quit = None
        display_dev_tools = False
        equation = []
        eq_index = 0
        hist_index = len(self.history)
        keypad = Keypad(2, 5, # x, y
                        7,8,9,' ','DEL',' ','CLS','',
                        4,5,6,' ','*','/',' ','~',
                        1,2,3,' ', '+','-',' ','h',
                        0,'.','?',' ','^', '=', ' ','q',
                        'n','i','r',' ','v',' ','<','>',
                        *Calculator.VARIABLES[0:26:]
                        )
        keypad.format(items_per_layer=8)

        # Just a divider to make it look nice
        tGame.render("\033[4H", "-"*10)

        while True:
            if display_dev_tools:
                tGame.render("\033[15;1H\033[2K",
                             "Cursor: ", str(eq_index))
                tGame.moveCursor('C', 2)
                tGame.render("Equation Length: ",str(len(equation)))
                tGame.moveCursor('C', 2)
                tGame.render("System: ", tGame.os.name)
                tGame.moveCursor('B', 1), tGame.moveCursor('D', 1000)
                tGame.render("\033[2K",
                             "hist_index: ", str(hist_index))
                tGame.moveCursor('C', 2)
                tGame.render("Mash counter: ", str(key_input.key_mash_counter))

            # Input mode
            tGame.render("\033[1;1H\033[2K\033[4m\033[1m\033[33m",
                         self.input_mode.name, "\033[0m")
            # Current equation being inputted
            tGame.render("\033[2;1H\033[2K",*map(str, equation))
            # Sets cursor to current position
            tGame.render(f"\033[2;{eq_index+1}H")
            tGame.renderCopy()

            key_input.keyIn()
            if key_input.pressed in (KEY.QUIT, KEY.K_q):
                return KEY.QUIT

            # KEYPAD input
            keypress = key_input.pressed
            if keypress in (CONTROLS.UP,CONTROLS.DOWN,CONTROLS.RIGHT,CONTROLS.LEFT,CONTROLS.ACTION):
                keypad_in = keypad.update(keypress)
                if str(keypad_in):
                    if keypad_in =='DEL':
                        keypress = KEY.BACKSPACE
                    elif keypad_in =='CLS':
                        keypress = CONTROLS.ESCAPE
                    else:
                        keypress = ord(str(keypad_in)) 

            # General input handling
            match keypress:
                case KEY.K_z:
                    display_dev_tools = not display_dev_tools
                    tGame.render("\033[14;1H\033[2K")
                case KEY.K_q:
                    return KEY.QUIT
                case KEY.K_h:
                    query_quit = help_message(key_input, True)
                case KEY.K_TILDE:
                    query_quit = self.ask_clear_data(key_input)

                # insert modes
                case KEY.K_n:
                    self.input_mode = Calculator.INPUT_MODES.APPEND
                    eq_index = max(0, len(equation)-1)
                case KEY.K_i:
                    self.input_mode = Calculator.INPUT_MODES.INSERT
                    query_quit = eq_index = self._insert_cursor(key_input, eq_index, len(equation)-1)
                case KEY.K_r:
                    self.input_mode = Calculator.INPUT_MODES.REPLACE
                    query_quit = eq_index = self._insert_cursor(key_input, eq_index, len(equation)-1)

                # history < goes deeper back > goes more recent
                case KEY.K_LESSER:
                    if len(self.history) > 0 and hist_index > 0:
                        self.flash_equation()
                        hist_index -= 1
                        equation = self.history[hist_index][:]
                        eq_index = len(equation)-1
                case KEY.K_GREATER:
                    if len(self.history) > 0 and hist_index < len(self.history):
                        self.flash_equation()
                        hist_index = min(len(self.history), hist_index+1)
                        equation = self.history[hist_index][:] if hist_index < len(self.history) else []
                        eq_index = max(0, len(equation)-1)
    
                # Attempt calculate current equation
                case KEY.ENTER | KEY.K_EQUALS | KEY.K_v:
                    self.history.append(equation[:])
                    try_calc = self.equation(equation)
                    hist_index = len(self.history)

                    try_calc = self.calculate(try_calc)
                    # Goes to 3rd line from top, clears it then displays answer or error message
                    tGame.render("\033[3;1H")
                    tGame.render("\033[2K", "= \033[32m")
                    tGame.render(str(try_calc[0]), "\033[0m")

                    # If not an error message
                    if len(try_calc) == 1:
                        self.variables[Calculator.ANS] = try_calc[0]

                        # Save to variable if calculate() is successful
                        if keypress == KEY.K_v:
                            tGame.moveCursor("B", 1000);tGame.moveCursor("D", 1000);
                            tGame.render("\033[1m\033[91m", "SET VALUE OF (A-Z) - keypad not available: ", "\033[0m")
                            tGame.renderCopy()
                            key_input.keyIn()
                            # Accepts only direct letter inputs, not Keypad presses
                            if (var := chr(key_input.pressed)) in Calculator.VARIABLES:
                                self.variables[var] = try_calc[0]
                                tGame.render(var, " = ", str(try_calc[0]))
                            else: tGame.render("\033[2K\033[1000D\033[1m\033[103m\033[31m",
                                               "CANCELED",
                                               "\033[0m")

                # Clear all
                case CONTROLS.ESCAPE:
                    self.flash_equation()
                    equation = []
                    eq_index = 0
                    hist_index = len(self.history)
                # Delete 
                case KEY.BACKSPACE:
                    hist_index = len(self.history)
                    self._eq_pop(equation, eq_index)
                    eq_index += 0 if (
                            self.input_mode==Calculator.INPUT_MODES.REPLACE and eq_index < len(equation) # len equation == max_index because of pop()
                            ) else -1
                    # Constrains index to 0-length of equation
                    eq_index = max(0, min(len(equation)-1, eq_index))

                # Displayable equation inputs (A-Z, ?, +-*/^, 0-9)
                case keypress if (
                        (num_in := chr(keypress))
                        in '.'+Calculator.NUMBERS+''.join(Calculator.OPERATORS)+''.join(Calculator.VARIABLES)):
                    hist_index = len(self.history)
                    self._eq_insert(equation, eq_index, num_in)
                    if len(equation) > 1:
                        eq_index += 0 if (
                                self.input_mode==Calculator.INPUT_MODES.REPLACE
                                )else 1

            if query_quit == KEY.QUIT:
                return KEY.QUIT

    # Reset saved data (does not save to file until program exit)
    def ask_clear_data(self, key_input):
                    tGame.moveCursor("B", 1000);tGame.moveCursor("D", 1000);tGame.render("\033[1m\033[6m\033[103m\033[31m")
                    tGame.render("THIS WILL RESET ALL DATA.")
                    tGame.moveCursor("A", 1);tGame.moveCursor("D", 1000)
                    tGame.render("Are you sure? y(es)/n(o)")
                    tGame.render("\033[0m")
                    tGame.renderCopy()
                    while True:
                        key_input.keyIn()
                        if key_input.pressed in (KEY.QUIT, KEY.K_q):
                            return KEY.QUIT
                        match key_input.pressed:
                            case KEY.K_y:
                                self.reset_data()
                                break
                            case KEY.K_n | CONTROLS.ESCAPE:
                                break
                    tGame.moveCursor("B", 1000);tGame.moveCursor("D", 1000);tGame.render("\033[2K");tGame.moveCursor("A", 1);tGame.render("\033[2K")
                    tGame.renderCopy()

    # Insert input cursor of the equation in "CURSOR MODE"
    def _insert_cursor(self, input_, index, max_index):
        tGame.render("\033[1;1H\033[2K\033[1m\033[4m",
                     "CURSOR MODE")
        tGame.render(f"\033[2;{index+1}H")
        tGame.renderCopy()
        while True:
            input_.keyIn()
            if input_.pressed in (KEY.QUIT, KEY.K_q):
                return KEY.QUIT
            match input_.pressed:
                case CONTROLS.LEFT:
                    index -= 1 if index > 0 else 0
                case CONTROLS.RIGHT:
                    index += 1 if index < max_index else 0
                case CONTROLS.ESCAPE | CONTROLS.ACTION | KEY.K_n | KEY.K_i | KEY.K_r:
                    return index

            tGame.render("\033[1;1H\033[2K\033[1m\033[4m",
                         "CURSOR MODE",
                         "\033[0m")
            tGame.render(f"\033[2;{index+1}H")
            tGame.renderCopy()

    # Insert item from equation based on input_mode
    def _eq_insert(self, equation: list, index: int, char: chr):
        match self.input_mode:
            case Calculator.INPUT_MODES.APPEND:
                equation.append(char)
            case Calculator.INPUT_MODES.INSERT:
                equation.insert(index, char)
            case Calculator.INPUT_MODES.REPLACE:
                if len(equation)>0: equation.pop(index)
                equation.insert(index, char)

    # Remove item from equation based on input_mode
    def _eq_pop(self, equation: list, index: int):
        if len(equation)<=0:
            return
        match self.input_mode:
            case Calculator.INPUT_MODES.APPEND:
                equation.pop()
            case Calculator.INPUT_MODES.INSERT:
                if index > 0:
                    equation.pop(index-1)
            case Calculator.INPUT_MODES.REPLACE:
                if len(equation) > 0:
                    equation.pop(index)

    # equation(list) returns list formatted for calculation
    def equation(self, equation: list):
        CalculatorEquation = []
        last_is_number = False
        for x in equation:
            if x in Calculator.OPERATORS:
                CalculatorEquation.append(x)
            elif x in Calculator.VARIABLES:
                CalculatorEquation.append(self.variables[x])
            else:
                if last_is_number:
                    CalculatorEquation.append(CalculatorEquation.pop()+x)
                else:
                    CalculatorEquation.append(x)
                last_is_number = True
                continue
            last_is_number = False

        return CalculatorEquation

    # Recursive function to simplify Equation list
    # Pretty much a case specific merge sort but less optimized
    # Errors will return (Error, int)
    #     int was supposed to be index of where the error occurred,
    #     but that does not really work with how the function is coded
    #     I would get rid of it, but its kind of needed for some checks
    def calculate(self, equation: list):
        if len(equation) == 0:
            return [0]
        if len(equation) == 2:
            return equation if equation[0] in (SyntaxError, ZeroDivisionError) else (SyntaxError, 0)
    
        # Exponents
        if "^" in equation:
            index = equation.index("^")
            try:
                result = float(equation[index-1]) ** int(equation[index+1])
                for _ in range(3):
                    equation.pop(index-1)
                equation.insert(index-1, result)
                equation = self.calculate(equation)
            except (IndexError, ValueError, SyntaxError):
                return (SyntaxError, index)
     
        # multi/divi and add/sub are pretty much copypasted
        # adding an extra function to do it would be kind of redundant
        # though, as there are only the two cases
        # Could edit it if brackets are added to the order of operations
        op1 = "*" in equation
        op2 = "/" in equation
        # checks to determine order of operations are hard-coded but speed and memory
        # are not really issues in this case since its just 2 operations
        if op1 or op2:
            if op1:
                index = index_op1 = equation.index("*")
                operation = operator.mul
            if op2:
                index = index_op2 = equation.index("/")
                operation = operator.truediv
            if op1 and op2:
                if index_op1 < index_op2:
                    index = index_op1 
                    operation = operator.mul
                else:
                    index = index_op2 
                    operation = operator.truediv
    
            try:
                result = operation(float(equation[index-1]), float(equation[index+1]))
                for _ in range(3):
                    equation.pop(index-1)
                equation.insert(index-1, result)
                equation = self.calculate(equation)
            except (IndexError, ValueError, SyntaxError):
                return (SyntaxError, index)
            except ZeroDivisionError:
                return (ZeroDivisionError, index)
    
        op1 = "+" in equation
        op2 = "-" in equation
        if (add:=("+" in equation)) or (sub:=("-" in equation)):
            if op1:
                index = index_op1 = equation.index("+")
                operation = operator.add
            if op2:
                index = index_op2 = equation.index("-")
                operation = operator.sub
            if op1 and op2:
                if index_op1 < index_op2:
                    index = index_op1 
                    operation = operator.add
                else:
                    index = index_op2
                    operation = operator.sub
    
            try:
                result = operation(float(equation[index-1]), float(equation[index+1]))
                for _ in range(3):
                    equation.pop(index-1)
                equation.insert(index-1, result)
                equation = self.calculate(equation)
            except (IndexError, ValueError, SyntaxError):
                return (SyntaxError, index)
    
        if len(equation) >= 2:
            return equation if equation[0] in (SyntaxError, ZeroDivisionError) else (SyntaxError, 0)
        if len(equation) == 1 and not (str(equation[0]) in "+-*/^"):
            try:
                # checks if number has multiple decimal points
                equation[0] = float(equation[0])
            except ValueError:
                return (SyntaxError, 0)
        return equation

    # Visual effect that equation is changing
    def flash_equation(self):
        tGame.render("\033[2;1H\033[2K",
                     " ")
        tGame.renderCopy()
        
        sleep(0.05)
        tGame.render("\033[2K")
        tGame.renderCopy()


class Keypad:
    LAYOUT = Enum('LAYOUT', 'HORIZONTAL VERTICAL')

    def __init__(self, x=1, y=1, *options):
        self.x = x
        self.y = y
    
        self.options = options
        self.size = len(options)
        self.index = 0
        self.old_index = self.index

        self.layout = Keypad.LAYOUT.HORIZONTAL
        self.items_per_layer = self.size
        self._layers = 1

    # Change the layout of the keypad
    # layout = LAYOUT.VERTICAL or LAYOUT.HORIZONTAL
    def format(self, layout=0, items_per_layer: int=0, x=0, y=0):
        if layout and layout in Keypad.LAYOUT:
            self.layout = layout
        if items_per_layer > 0 and items_per_layer <= self.size:
            self.items_per_layer = items_per_layer
            self._layers = self.size//items_per_layer+(1 if self.size%items_per_layer else 0)
        if x: self.x = x
        if y: self.y = y

    def update(self, input_):
        # Inputs UP DOWN RIGHT LEFT ARROW KEYS
        # SPACE TO SELECT
        match input_:
            case CONTROLS.ACTION:
                displace = 0
            case CONTROLS.UP:
                displace = -self.items_per_layer if (
                        self.layout == Keypad.LAYOUT.HORIZONTAL
                        ) else -1
            case CONTROLS.DOWN:
                displace = self.items_per_layer if (
                        self.layout == Keypad.LAYOUT.HORIZONTAL
                        ) else 1
            case CONTROLS.RIGHT:
                displace = self.items_per_layer if (
                        self.layout == Keypad.LAYOUT.VERTICAL
                        ) else 1
            case CONTROLS.LEFT:
                displace = -self.items_per_layer if (
                        self.layout == Keypad.LAYOUT.VERTICAL
                        ) else -1
        self._move_index(displace)

        # Displaying Keypad
        for i in range(self._layers):
            tGame.render(f"\033[{self.y+i};{self.x}H")
            for j in range(self.items_per_layer):
                # layers through times items per layer
                # plus the depth into the layer
                index = i*self.items_per_layer+j
                # Failsafe if last layer has fewer elements than the rest
                if index > self.size-1:
                    break

                option = self.options[index]
                if index == self.index:
                    tGame.render("\033[107m\033[30m", str(option), "\033[0m")
                else:
                    tGame.render(str(option))
        return self.options[self.index] if displace == 0 else ""

    def _move_index(self, displacement):
        self.old_index = self.index
        # displacement = +/-1 going side to side and
        # +/-items_per_row going across layers
        self.index = self.index + displacement

        if not (self.index in range(0, self.size)):
            if displacement == -1:
                self.index = self.size-1
            elif displacement == 1:
                self.index = 0
            else:
                # Constrains index to being within list if last layer
                # has fewer elements than the rest
                self.index = min(self.size-1,
                                 self.old_index - (
                                 (displacement>0)-(displacement<0) # Gets +/-sign of int
                                 )*
                                 (self._layers-1)*self.items_per_layer)
            if self.index < 0:
                self.index = self.size-1

        if not str(self.options[self.index]).strip():
            self._move_index((displacement>0)-(displacement<0))

def help_message(input_, use_tGame_flag):
    # \033[1000D just sets the cursor to the left so it prints properly
    # on all terminals (certain terminals do not properly parse formatted
    # strings - """\n""")
    # was too lazy, so I just copy-pasted it at the beginning of each line
    message = (
    """

\033[1000D      ^
\033[1000D    < + > - arrow keys to move cursor (input pad)
\033[1000D      v

\033[1000D    SPACE
\033[1000D        - SPACE to select in keypad

\033[1000D    Can either directly type in equation (e.g "1+1")
\033[1000D    or use arrow keys and SPACE to select
\033[1000D    Keypad is hidden by default until arrow keys are pressed

\033[1000D    q
\033[1000D        - 'q' to save and quit
\033[1000D    CTRL+c
\033[1000D        - control-C to exit at any point
\033[1000D    CTRL+ALT+c
\033[1000D        - control-alt-C to invoke an error (i.e force quit program)
\033[1000D          NOT RECOMMENDED unless q/CTRL+c do not work as it will not save work
\033[1000D          May only work on some terminals
\033[1000D
\033[1000D    h 'h' to show this screen again

\033[1000D       1/4 ->
    """,

    """

\033[1000D    0-9
\033[1000D        - numbers to input digit
\033[1000D    A-Z, ?
\033[1000D        - capital letters or question mark (ANS) to input variables
\033[1000D    [+, -, *, /, ^]
\033[1000D        - operators to input operator
\033[1000D    RETURN/ENTER, =
\033[1000D        - return/enter or '=' to calculate equation
\033[1000D    ESC
\033[1000D        - escape to clear input
\033[1000D
\033[1000D    <- 2/4 ->
\033[1000D    """,

    """

\033[1000D    n
\033[1000D        - 'n' to revert to 'append/normal mode' (default)
\033[1000D          edit current equation by adding to the end of it
\033[1000D    i
\033[1000D        - 'i' to turn on 'insert mode'
\033[1000D          Enters Cursor Mode to place cursor
\033[1000D          n, i, r, ESC, or SPACE to confirm new cursor position 
\033[1000D          edit current equation by inserting left of cursor
\033[1000D    r
\033[1000D        - 'r' to turn on 'replace mode'
\033[1000D          Enters Cursor Mode to place cursor
\033[1000D          n, i, r, ESC, or SPACE to confirm new cursor position 
\033[1000D          edit current equation by replacing right (under) of cursor

\033[1000D    < - > - left and right key to move cursor (Cursor Mode)
\033[1000D
\033[1000D    <- 3/4 ->

    """,
    """

\033[1000D    < or >
\033[1000D        - '<' or '>' to go back and forth between previous equations
\033[1000D    v [variable]
\033[1000D        - 'v' then the name of a variable (A-Z) 
\033[1000D              to store the value of the current equation in [variable]
\033[1000D          Press any other key to cancel
\033[1000D          Attempting to store an error will not work
\033[1000D    ~ [y/n to confirm]
\033[1000D        - '~' (tilde) to reset data (history and variables)
\033[1000D          Press y to confirm and n or ESC to cancel
\033[1000D          Variables default to 0 if no value is stored
\033[1000D
\033[1000D    <- 4/4 -> (exit)
    """
    )

    if not use_tGame_flag:
        for i in range(3):
            input(message[i])
        return

    current_page = 0
    LAST_PAGE = len(message)-1

    # saves the current output buffer of terminal
    tGame.render("\033[?1049h")
    tGame.renderCopy()
    while current_page <= LAST_PAGE:
        # Display page //
        tGame.screenClear()
        tGame.render("\033[1;1H")
        tGame.render(message[current_page])
        tGame.renderCopy()
        # \\

        input_.keyIn()

        if input_.pressed in (KEY.QUIT, KEY.K_q):
            return KEY.QUIT
        if input_.pressed == CONTROLS.ESCAPE:
            break

        match input_.pressed:
            case CONTROLS.UP | CONTROLS.LEFT:
                current_page = current_page-1 if current_page > 0 else 0
            case CONTROLS.DOWN | CONTROLS.RIGHT:
                current_page += 1
            case CONTROLS.ESCAPE:
                current_page = LAST_PAGE+1
    # sets cursor to (x, y): (1,1) to print properly
    tGame.screenClear()
    tGame.render("\033[1;1H")
    # restore old terminal window output
    tGame.render("\033[?1049;1l")
    tGame.renderCopy()
        
if __name__ == "__main__":
    main()
    tGame.screenClear()
    tGame.renderCopy()
