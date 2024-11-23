import os
from random import randint

MONTH_NAMES = ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december')

def clearScreen():
    os.system("clear" if os.name == 'posix' else "cls")

def date_str(date_list): # dmyyyy to yyyymmdd
    return '0'*(4-len(date_list[2])) + date_list[2] + '0'*(2-len(date_list[1])) + date_list[1] + '0'*(2-len(date_list[0])) + date_list[0] 

def merge(left_list, right_list):
    lIndex = 0
    rIndex = 0
    
    merged_list = []

    while lIndex < len(left_list) and rIndex < len(right_list):
        left = left_list[lIndex]
        left_date = int(date_str(left[1:4]))
        right = right_list[rIndex]
        right_date = int(date_str(right[1:4]))

        if left_date <= right_date:
            lIndex += 1
            merged_list.append(left)
        else:
            rIndex += 1
            merged_list.append(right)

    # Append leftover items
    if lIndex != len(left_list):
        for reminder in left_list[lIndex:len(left_list)]:
            merged_list.append(reminder)
    if rIndex != len(right_list):
        for reminder in right_list[rIndex:len(right_list)]:
            merged_list.append(reminder)

    return merged_list

def sort_reminders(reminders: list): # Sorts using int(yyyymmdd) - checks year first since it is largest, then month, then day
    length = len(reminders)
    if length == 1:
        return reminders

    left = sort_reminders(reminders[0:length//2])
    right = sort_reminders(reminders[length//2:length])

    return merge(left, right)

def input_reminder():
    clearScreen()
    print()
    reminder = input("Name: ")
    while True:
        year = input("Year: ")
        if year.isdigit():
            year = str(int(year))
            break
    while True:
        month = input("Month: ")
        if (month.isdigit() and 1<=int(month)<=12):
            # strips leading zero if inputted
            month = str(int(month))
            break
        elif month.lower() in MONTH_NAMES:
            month = str(MONTH_NAMES.index(month.lower())+1)
            break
    while True:
        day = input("Day: ")
        if day.isdigit():
            if (month == '2' and int(day)==29):
                if (int(year) % 4 == 0):
                    # strips leading zero if inputted
                    day = str(int(day))
                    break
                else:
                    continue

            elif (1<=int(day)<=30 and month in "4 6 9 11".split()) or (
                  1<=int(day)<=31 and month in "1 3 5 7 8 10 12".split()) or (
                  1<=int(day)<=28 and month == '2'):
                # strips leading zero if inputted
                day = str(int(day))
                break

    # Stores day month year
    return [reminder, day, month, year]

def reminder_remove(reminder_list):
    # How far down to scroll when list overflows screen
    scroll_level = 0
    scroll_restart = -1
    
    while True:
        clearScreen()
        display_reminders(reminder_list, colour_picker=[91 for _ in reminder_list], start=scroll_level, end=scroll_restart)
        if len(reminder_list) == 0:
            input("List is empty\n\n[ENTER]")
            break
        try:
            item_number = input("\033[2;1HRemove reminder (integer)\nor other to cancel\n\n(<) previous\n(>) next\n\n> ")
            if item_number == '>':
                scroll_level += 1
                scroll_restart += 1 if scroll_restart != -1 else 2
                if scroll_level >= len(reminder_list):
                    scroll_level -= len(reminder_list)
                    scroll_restart = -1
                continue
            elif item_number == '<':
                scroll_level -= 1
                scroll_restart -= 1
                if scroll_level <= -1:
                    scroll_level += len(reminder_list)
                    scroll_restart = len(reminder_list)-1
                continue

            item_number = int(item_number)

            if not (0 < item_number <= len(reminder_list)):
                input(f"Number should be: 0 < (input) < {len(reminder_list)+1}\n\n[ENTER]")
                continue
            r_item = reminder_list[item_number-1][:]
            reminder_list.pop(item_number-1)
            return r_item
        except (ValueError):
            input("Nothing removed\n\n[ENTER]")
            return 0

'''
display_reminders(reminder_list - list of reminder objects -> lists of [name, day, month, year]
                  start - index of first reminder to display | default: 0
                  end - index of last reminder to display (non-inclusive) | default: -1 (last item)
'''
def display_reminders(reminder_list, colour_picker=[],start=0, end=-1):
    # print ToDo list at (30, 2)
    print("\033[2;30H", end='')

    if end == -1:
        temp_list = reminder_list[start:]
    elif end <= start:
        temp_list = reminder_list[start:len(reminder_list)]+reminder_list[0:end]
    else:
        temp_list = reminder_list[start:end]

    # colourpicker defaults to white
    colour_picker = colour_picker if colour_picker else [0 for _ in reminder_list]
    # Bolds first item
    print("\033[1m", end='')

    # Max screen width for preventing overflow
    max_width = os.get_terminal_size().columns-35

    i = start
    for reminder in temp_list:
        i += 1

        # Colour
        print(f"\033[38;5;{colour_picker[i-1]}m", end='')

        # Reminder Name
        print(str(i) + '. ' + reminder[0][0:max_width]+("..." if len(reminder[0])>=max_width else ''), end='\033[1B')

        # Reminder Date
        print("\033[34G", end='')
        reminder_date = f"{MONTH_NAMES[int(reminder[2])-1].capitalize()} {reminder[1]}, {reminder[3]}"
        print(reminder_date[0:max_width-4] + ("..." if len(reminder_date)>max_width-4 else ''), end='\033[1B')

        # Resets colour to white
        print(f"\033[0m", end='')

        print("\033[30G" + '_'*max_width, end='\033[2B')
        print("\033[30G\033[2m", end='')

        # Sets i beginning of list (0+1) if {end} less than {start}
        if i == len(reminder_list): i=0
        
    print(f"\033[0m", end='')


def main():
    print("\033[?1049h")
    print("\033]0;Quarter-To\x07")
    clearScreen()

    reminders = []
    deleted_reminder = None

    colour_picker = []
    COLOUR_RANGE = (17, 231)

    try:
        with open("data.txt", 'r') as f:
            line = f.readline()
            while line: # while not end of file
                reminders.append(line.split())
                colour_picker.append(randint(*COLOUR_RANGE))
                line = f.readline()
    except FileNotFoundError:
        open("data.txt", 'w')

    # How far down to scroll when list overflows screen
    scroll_level = 0
    scroll_restart = -1

    while True:
        clearScreen()
        
        display_reminders(reminders, colour_picker=colour_picker, start=scroll_level, end=scroll_restart)

        # Print recently deleted if exists
        if deleted_reminder:
            print("\033[14;1H\033[31m\033[1m"+
                  "Recently Deleted:")        
            print(deleted_reminder[0][0:25]+("..." if len(deleted_reminder[0]) > 27 else ""), end='\033[1B')
            print("\033[4G", end='')
            date_print = f"{MONTH_NAMES[int(deleted_reminder[2])-1].capitalize()} {deleted_reminder[1]}, {deleted_reminder[3]}"
            print(date_print[0:22]+("..." if len(date_print)>24 else ""), end='\033[1B') 
        print("\033[0m", end='')

        # User input main screen
        print("\033[2;1H(a)dd reminder\n(r)emove reminder\n(s)ort reminder\n(u)ndo delete\n(q)uit\n\n(<) previous\n(>) next\n")
        main_action = input("> ")
        if len(main_action) == 0:
            continue
        match main_action.lower()[0]:
            case 'q':
                break
            case 'a':
                reminders.append(input_reminder())
                colour_picker.append(randint(*COLOUR_RANGE))
            case 'r':
                deleted_reminder = reminder_remove(reminders)
                if deleted_reminder: colour_picker.pop()
            case 's':
                reminders = sort_reminders(reminders)
            case 'u':
                if deleted_reminder:
                    reminders.append(deleted_reminder)
                    colour_picker.append(randint(*COLOUR_RANGE))
                    deleted_reminder = None
            case '>':
                scroll_level += 1
                scroll_restart += 1 if scroll_restart != -1 else 2
                if scroll_level >= len(reminders):
                    scroll_level -= len(reminders)
                    scroll_restart = -1
            case '<':
                scroll_level -= 1
                scroll_restart -= 1
                if scroll_level <= -1:
                    scroll_level += len(reminders)
                    scroll_restart = len(reminders)-1

    with open("data.txt", 'w') as f:
        for reminder in reminders:
            f.write(" ".join(reminder)+'\n')
        
    print("\033[?1049;1l")
main()
