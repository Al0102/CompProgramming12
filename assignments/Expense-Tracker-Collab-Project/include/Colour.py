from enum import Enum, auto

AVAILABLE_COLOURS = ("BLACK","RED","GREEN","YELLOW","BLUE","MAGENTA","CYAN","WHITE")
FOREGROUND = {AVAILABLE_COLOURS[i]:f"\033[3{i}m" for i in range(len(AVAILABLE_COLOURS))}
BACKGROUND = {AVAILABLE_COLOURS[i]:f"\033[4{i}m" for i in range(len(AVAILABLE_COLOURS))}
RESET = "\033[0m"


def contrastRGB(colour_rgb:tuple):
    sum_colour = sum(colour_rgb)
    maxi = max(colour_rgb)
    mini = min(colour_rgb)
    if (maxi+mini > 150 and maxi - mini > 100) or sum_colour > 300:
        return (255-max(bit8, 50) for bit8 in colour_rgb)
    else:
        return (255-bit8 for bit8 in colour_rgb)


def contrast8Bit(colour_8Bit):
    if 16 > colour_8Bit:
        return 15 if colour_8Bit in (0,8) else 0
    elif 15 < colour_8Bit and 232 > colour_8Bit: 
        return 15 if (colour_8Bit-16)%36 < 18 else 0
    return 15 if colour_8Bit < 244 else 0


COLOUR_OPTION = Enum("COLOUR_OPTION", "FOREGROUND BACKGROUND AUTO_FRONT AUTO_BACK")


def getCodeRGB(colour_rgb, option):
    match option:
        case COLOUR_OPTION.FOREGROUND:
            foreground = "\033[38;2;{};{};{}m".format(*colour_rgb)
            background = ""
        case COLOUR_OPTION.BACKGROUND:
            background = "\033[48;2;{};{};{}m".format(*colour_rgb)
            foreground = ""
        case COLOUR_OPTION.AUTO_FRONT:
            foreground = "\033[38;2;{};{};{}m".format(*colour_rgb)
            background = "\033[48;2;{};{};{}m".format(*contrastRGB(colour_rgb))
        case COLOUR_OPTION.AUTO_BACK:
            background = "\033[48;2;{};{};{}m".format(*colour_rgb)
            foreground = "\033[38;2;{};{};{}m".format(*contrastRGB(colour_rgb))

    return foreground+background


def getCodeBasic(colour_4Bit, option, bright=False):
    if isinstance(colour_4Bit, str):
        colour_4Bit = AVAILABLE_COLOURS.index(colour_4Bit)
    brightness = 9 if bright else 3
    match option:
        case COLOUR_OPTION.FOREGROUND:
            foreground = "\033[{}{}m".format(brightness, colour_4Bit)
            background = ""
        case COLOUR_OPTION.BACKGROUND:
            background = "\033[{}{}m".format(brightness+1, colour_4Bit)
            foreground = ""
        case COLOUR_OPTION.AUTO_FRONT:
            foreground = "\033[{}{}m".format(brightness, colour_4Bit)
            background = "\033[{}{}m".format(brightness+1, 0 if colour_4Bit in (3,7) else 7)
        case COLOUR_OPTION.AUTO_BACK:
            background = "\033[{}{}m".format(brightness+1, colour_4Bit)
            foreground = "\033[{}{}m".format(brightness, 0 if colour_4Bit in (3,7) else 7)
    return foreground+background


def getCode8Bit(colour_8Bit, option):
    match option:
        case COLOUR_OPTION.FOREGROUND:
            foreground = "\033[38;5;{}m".format(colour_8Bit)
            background = ""
        case COLOUR_OPTION.BACKGROUND:
            background = "\033[48;5;{}m".format(colour_8Bit)
            foreground = ""
        case COLOUR_OPTION.AUTO_FRONT:
            foreground = "\033[38;5;{}m".format(colour_8Bit)
            background = "\033[48;5;{}m".format(contrast8Bit(colour_8Bit))
        case COLOUR_OPTION.AUTO_BACK:
            background = "\033[48;5;{}m".format(colour_8Bit)
            foreground = "\033[38;5;{}m".format(contrast8Bit(colour_8Bit))
    return foreground+background

if __name__ == "__main__":
    import random
    for _ in range(1):
        #print(getCodeRGB(tuple(random.randint(0,255) for _ in range(3)), COLOUR_OPTION.AUTO_BACK)+"Hello World\033[0m")
        print(getCodeBasic(random.randint(0,7), COLOUR_OPTION.AUTO_FRONT)+"Hello World\033[0m")
        print(getCode8Bit(random.randint(0,255), COLOUR_OPTION.AUTO_FRONT)+"Hello World\033[0m")
