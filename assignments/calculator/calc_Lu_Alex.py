import sys
import KEY, CONTROLS
import tGame

def main():
    tGame.init()
    key_input = tGame.KeyboardInput()

    while True:
        key_input.keyIn()
        if key_input.pressed == KEY.QUIT:
            return

        tGame.renderCopy()

if __name__ == "__main__":
    main()
