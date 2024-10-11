import sys
import operator
import KEY, CONTROLS
import tGame

"""
list<float> calculate(equation: list)
    returns calculated equation as list of ints
tuple<Error, int> calculate(equation: list)
    returns an tuple containing the error that occurred while parsing and the index where it occurs

void help_message(use_tGame_flag=True)
    displays help message
        parameters:
            use_tGame_flag
                displays using tGame.render() if set to True and print if false
                default: True
"""

def main():
    input(
    """
    This program uses keyboard inputs and may take control
        of the terminal window/IO streams.
        Although it should return everything to normal upon
        program exit, there is a chance that I missed a bug
        somewhere so use at your own risk.

        [enter]

    """
    )
    accept_flag = 0
    for _ in range(20):
        confirm_open_calculator = input(
            "> I understand and wish to continue (y/n)"
            ).lower()
        match confirm_open_calculator:
            case 'n':
                break
            case 'y':
                accept_flag = 1
                break
    if not accept_flag:
        return 0

    try:
        tGame.init()
        key_input = tGame.KeyboardInput()
        tGame.render("\033]0;Calcalexor\x07")

        if help_message(key_input) == KEY.QUIT:
            return

        while True:
            key_input.keyIn()
            if key_input.pressed == KEY.QUIT:
                return
            if key_input.pressed == CONTROLS.ESCAPE:
                tGame.screenClear()

            match key_input.pressed :
                case KEY.K_h:
                    help_message(key_input)

            tGame.renderCopy()

    finally:
        if tGame.POSIX:
            import tty, termios
            termios.tcsetattr(tGame.fd,termios.TCSADRAIN, tGame.old_settings)

def calculate(equation: list):
    if len(equation) == 0:
        return [0]
    if len(equation) == 1 and not (str(equation[0]) in "+-*/^"):
        return equation
    if len(equation) == 2:
        return equation if equation[0] == SyntaxError else (SyntaxError, 0)

    if "^" in equation:
        index = equation.index("^")
        try:
            result = float(equation[index-1]) ** int(equation[index+1])
            for _ in range(3):
                equation.pop(index-1)
            equation.insert(index-1, result)
            equation = calculate(equation)
        except (IndexError, ValueError, SyntaxError):
            return (SyntaxError, index)
 
    op1 = "*" in equation
    op2 = "/" in equation
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
            equation = calculate(equation)
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
            equation = calculate(equation)
        except (IndexError, ValueError, SyntaxError):
            return (SyntaxError, index)

    return equation



def help_message(input_, use_tGame_flag):
    message = (
    """

      ↑
    ← . → - arrow keys to move cursor (input pad)
      ↓

    ← →   - left and right key to move cursor (insert/replace mode)


    q
    - 'q' to save and quit
    CTRL+c
    - control-C to exit at any point
    CTRL+ALT+c
    - control-alt-C to invoke an error (i.e force quit program)
          NOT RECCOMMENDED unless q/CTRL+c do not work
          May only work on some terminals

    h 'h' to show this screen again

       1/3 ->
    """,

    """

    0-9
    - numbers to input digit
    A-Z
    - capital letters to input variables
    [+, -, *, /, ^]
    ↵
    - return/enter to calculate equation
    ESC
    - escape to clear input

    <- 2/3 ->
    """,

    """

    i
    - 'i' to toggle 'insert mode'
      edit current equation by inserting left of cursor
    r
    - 'r' to toggle 'replace mode'
      edit current equation by replacing right of cursor
    v [variable]
    - 'v' then the name of a variable (A-Z) to view the value of [variable]
    s [variable] [value]
    - 's' then the name of a variable (A-Z) to store [value] in [variable]
          Press return/enter to confirm
          Defaults to 0 if no value is stored or if invalid value is passed

    <- 3/3 ->
    """
    )

    if not use_tGame_flag:
        for i in range(3):
            input(message[i])
        return

    current_page = 0
    LAST_PAGE = 2
    tGame.render("\033[?1049h")
    tGame.renderCopy()
    while current_page <= last_page:
        tGame.screenClear()
        tGame.render("\033[2;1H")
        tGame.render(message)
        tGame.renderCopy()

        input_.keyIn()

        if key_input.pressed == KEY.QUIT:
            return KEY.QUIT
        if key_input.pressed == CONTROLS.ESCAPE:
            tGame.screenClear()
            tGame.render("\033[1;1H")
            tGame.render("\033[?1049;1l")
            tGame.renderCopy()
            return

        match key_input.pressed :
            case CONTROLS.UP:
        
        return

if __name__ == "__main__":
    main()