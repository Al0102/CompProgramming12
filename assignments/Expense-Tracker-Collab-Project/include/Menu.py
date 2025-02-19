import sys, os
from enum import Enum
import KEY, CONTROLS
import tGame
from Colour import getCodeRGB, COLOUR_OPTION


class Keypad:
    LAYOUT = Enum('LAYOUT', 'HORIZONTAL VERTICAL')
    ALIGN = Enum('ALIGN', 'LEFT CENTER RIGHT')
    FIT = Enum('FIT', 'TIGHT SIMILAR')

    def __init__(self, options: iter):
        self.x = 1
        self.y = 1
    
        self._options = list(options)
        self.size = len(options)
        self.index = 0
        self.old_index = self.index

        self.layout = Keypad.LAYOUT.HORIZONTAL
        self.items_per_layer = self.size
        self._layers = 1

        self.text_align = Keypad.ALIGN.LEFT
        self.padding = 0
        self.fit = Keypad.FIT.TIGHT
        self.text_colour = [255,255,255]

    '''
    def format(layout, items_per_layer, x, y,
               text_align, padding, fit, text_colour, select_colour)
        Change the layout of the keypad

        Parameters:
        layout: LAYOUT.VERTICAL or LAYOUT.HORIZONTAL
        items_per_layer: 1 <= (int) <= length of options
          - options allowed before wrapping to next layer
        x, y: (int), (int)
          - coordinate to display keypad (topleft)
        text_align: ALIGN.LEFT, ALIGN.CENTER, or ALIGN.RIGHT
        padding: (int)
          - spacing between options
        fit: FIT.TIGHT or FIT.SIMILAR
          - fit of horizontal options
          - e.g. FIT.TIGHT: startoptions
                            helpquit
                 FIT.SIMILAR: start  options
                              help   quit
        text_colour: (r,g,b) 0 <= rgb <= 255
    '''
    # TODO
    # - formatting for text-align
    # - fit
    def format(self, layout=0, items_per_layer: int=0, x=0, y=0,
               text_align=0, padding=0, fit=0, text_colour=0):
        if layout:
            if not layout in Keypad.LAYOUT:
                raise Exception(f"Invalid layout option: {layout}. Should be of type Keypad.LAYOUT (HORIZONTAL or VERTICAL)")
            self.layout = layout

        if items_per_layer:
            if not (items_per_layer > 0 and items_per_layer <= self.size):
                raise Exception(f"Invalid value for items_per_layer: {items_per_layer}. Should be 0 < (int) <= len(self._options)")
            self.items_per_layer = items_per_layer
            self._layers = self.size//items_per_layer+(1 if self.size%items_per_layer else 0)
        if x: self.x = int(x)
        if y: self.y = int(y)

        if text_align:
            if not text_align in Keypad.ALIGN:
                raise Exception(f"Invalid text_align option: {text_align}. Should be of type Keypad.ALIGN (LEFT,CENTER,or RIGHT)")
            self.text_align = text_align

        if padding: self.padding = int(padding)
        if fit and fit in Keypad.FIT:
            self.fit = fit

        try:
            if text_colour:
                for i in range(3):
                    self.text_colour[i] = int(text_colour[i])
        except (IndexError, ValueError):
            raise Exception("Incorrect format for RGB: should be tuple/list of 3 integers")

    def draw(self):
        '''
        Horizontal Layout
          0 1 2
          3 4 5
        rows: 2; columns: 3
        Vertical Layout
          0 3
          1 4
          2 5
        rows: 3; columns: 2
        '''
        rows = self._layers if self.layout==Keypad.LAYOUT.HORIZONTAL else self.items_per_layer
        columns = self.items_per_layer if self.layout==Keypad.LAYOUT.HORIZONTAL else self._layers

        tGame.render(getCodeRGB(self.text_colour, COLOUR_OPTION.FOREGROUND))
        for i in range(rows):
            tGame.render(f"\033[{self.y+i+i*self.padding};{self.x}H")


            for j in range(columns):
                # layers through times items per layer
                # plus the depth into the layer
                if self.layout == Keypad.LAYOUT.HORIZONTAL:
                    index = i*self.items_per_layer+j
                else: # Keypad.LAYOUT.VERTICAL
                    index = i+self.items_per_layer*j
                # Failsafe if last layer has fewer elements than the rest
                if index > self.size-1:
                    break

                # Sets highlight for currently hovered option
                option = self._options[index]
                if index == self.index:
                    tGame.render(getCodeRGB(self.text_colour, COLOUR_OPTION.AUTO_BACK), str(option), "\033[0m",getCodeRGB(self.text_colour, COLOUR_OPTION.FOREGROUND))
                else:
                    tGame.render(str(option))

                # Padding
                if j < columns-1:
                    tGame.moveCursor('C', self.padding)

        # Reset text style after keypad
        tGame.render("\033[0m")


    def update(self, input_, draw=True):
        # Inputs UP DOWN RIGHT LEFT ARROW KEYS
        # SPACE TO SELECT
        submit = False
        match input_:
            case input_ if input_ in CONTROLS.ACTION:
                submit = True
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
            case _:
                return None
        self._move_index(displace)

        # Displaying Keypad
        if draw: self.draw()

        # Pressed action key returns current option (str)
        # Directional input returns Non
        return (self.index,self._options[self.index]) if submit else None

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

        if not str(self._options[self.index]).strip():
            self._move_index((displacement>0)-(displacement<0))


class OptionScreen:
  
    def __init__(self, choices=[], functions=[]):
        if len(choices) != len(functions):
            raise Exception("lengths of choices and function do not match")

        self.choices = {choices[i]: functions[i] for i in range(len(choices))}

        window_size = os.get_terminal_size()
        display_centered = ((window_size[0]-len(max(self.choices.keys(), key=len)))//2,
                            window_size[1]//len(self.choices))

        self.keypad = Keypad(self.choices.keys())
        self.keypad.format(items_per_layer=1,
                           layout=Keypad.LAYOUT.HORIZONTAL,
                           x=display_centered[0],
                           y=display_centered[1],
                           text_align=Keypad.ALIGN.CENTER,
                           padding=1,
                           text_colour=(0,255,0))

    def open_menu(self, Input: tGame.KeyboardInput):
        self.keypad.draw()
        tGame.renderCopy()

        while True:
            Input.keyIn()
            
            if Input.pressed == CONTROLS.ESCAPE:
                self.close_menu()
                return 0

            if Input.pressed in (CONTROLS.UP, CONTROLS.DOWN, CONTROLS.ACTION):
                selected = self.keypad.update(Input.pressed)
                tGame.renderCopy()
                if selected != None:
                    # Runs the function corresponding to the selection
                    # If function returns KEY.QUIT, close the menu
                    if self.choices[selected[1]]() == KEY.QUIT:
                        self.close_menu()
                        return selected

        tGame.renderCopy()

    def close_menu(self, save_cursor_position=False):
        if not save_cursor_position:
            self.keypad.index = 0
    
if __name__ == "__main__":
    x = 0
    tGame.init()
    key = tGame.KeyboardInput()
    main_menu = Keypad(
            ["Add Expense", "Remove Expense", "View Expense", "Exit"])
    main_menu.format(x=2,y=7,
                          layout=Keypad.LAYOUT.VERTICAL,
                          text_colour=(100,100,150))

    while x < 100:
        tGame.renderCopy()
        key.keyIn()
        if main_menu.update(key.pressed):
            break
        x +=1

    tGame.end()
