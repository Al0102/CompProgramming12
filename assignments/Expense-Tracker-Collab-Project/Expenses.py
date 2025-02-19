import json
import os,sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "./include"))
import tGame, CONTROLS, KEY, Colour
from Menu import Keypad

MONTH_NAMES = ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december')

HINT_COLOUR = Colour.getCodeRGB((170, 105, 87), Colour.COLOUR_OPTION.FOREGROUND)
INVALID_COLOUR = Colour.getCodeBasic("RED", Colour.COLOUR_OPTION.AUTO_BACK)
MONEY_COLOUR = Colour.getCodeRGB((210,255,205), Colour.COLOUR_OPTION.AUTO_BACK)
DATE_COLOUR = Colour.getCodeRGB((210,205,255), Colour.COLOUR_OPTION.AUTO_BACK)

ORIGIN_POS = (2,2)

class ExpensesApp:
    def __init__(self):
        self.key_in = tGame.KeyboardInput()

        self.main_menu = Keypad(
                ["Add Expense", "Remove Expense", "View Expenses", "Total Expense", "Exit"])
        self.main_menu.format(x=ORIGIN_POS[0],y=ORIGIN_POS[1]+5,
                              layout=Keypad.LAYOUT.VERTICAL,
                              text_colour=(100,100,150))
        self.remove_menu = Keypad(
                ["Back to Input", "View Expenses", "Exit"])
        self.remove_menu.format(x=ORIGIN_POS[0],y=ORIGIN_POS[1]+3,
                              layout=Keypad.LAYOUT.HORIZONTAL,
                              padding=2,
                              text_colour=(100, 20, 7))

        self.expenses_list = dict()
        self.load_data()

    def __del__(self):
        tGame.end()
        
    def run(self):
        tGame.setTitle("Expense tracker") # Window title

        tGame.screenClear()
        tGame.setCursor(*ORIGIN_POS) # positions start topleft at (1,1)
        tGame.render("Welcome to expense tracker!\n"+"_"*29) # Appends to tGame.render_buffer (str)

        tGame.renderCopy() # sys.stdout.write(tGame.render_buffer)
        # tGame.render_buffer contains anything from tGame.render() (check tGame.py)
        first_entry = True

        while True:
            tGame.hideCursor()

            tGame.moveCursor('B', 2)
            tGame.setCursor(2)
            tGame.render("What would you like to do?")

            ExpensesApp.help_display(35,2, "Main")

            self.main_menu.index = 0 # Sets current choice to first option
            self.main_menu.draw() # Draws before the blocking input call

            tGame.renderCopy()

            while True:
                # Clears input prevents accidental choice (from holding button)
                self.key_in.clearPipe()

                # Redraws by default
                action = self.main_menu.update(self.key_in.keyNext()) 

                # Neither Keypad.draw nor Keypad.update call this automatically
                tGame.renderCopy() 

                # CONTROLS.ACTION wasn't pressed, nothing selected
                if not action: 
                    continue
                else:
                    if first_entry: self.main_menu.format(y=ORIGIN_POS[1]+3)
                    break
                    
            # Keypad.update() returns tuple: (choice_index, choice_name)
            # choice_index is used bc it has to be unique, unlike choice_name
            match action[0]: 
                case 0:
                    self.add_expense() # New scene
                case 1:
                    self.remove_menu.index = 0 # Sets to first option in menu
                    self.remove_expense() # New scene
                case 2:
                    tGame.setCursor(ORIGIN_POS[0],12) # Displays expenses below main menu
                    tGame.renderCopy()
                    self.view_expenses()
                case 3:
                    self.expense_summary() #shows expense total
                case 4:
                    self.save_data()
                    return # Quit app
            time.sleep(0.1)
            tGame.screenClear()
            tGame.setCursor(1,1)

    def view_expenses(self):
        tGame.screenClear()
        tGame.setCursor(*ORIGIN_POS)

        if len(self.expenses_list) == 0: 
            tGame.render("You currently have no expenses.")
        else:
            for category, expenses in self.expenses_list.items():
                reminder_number = 1
                tGame.setCursor(ORIGIN_POS[0])
                tGame.render("Category: "+category+'\n'+'-'*30+'\n')

                for expense in expenses:
                    # Expense name
                    tGame.setCursor(ORIGIN_POS[0]+2)
                    tGame.render(f"{reminder_number}. {expense['name']}\n")
                    # Cost
                    tGame.setCursor(ORIGIN_POS[0]+4)
                    tGame.render(f"{MONEY_COLOUR}Amount:{Colour.RESET} ${expense['amt']}\n")
                    # Date of expense
                    tGame.setCursor(ORIGIN_POS[0]+4)
                    tGame.render(f"{DATE_COLOUR}Date:{Colour.RESET} {MONTH_NAMES[expense['date'][1]-1].title()} {expense['date'][2]}, {expense['date'][0]}\n\n")
                    reminder_number+=1

        tGame.render('\n')
        tGame.setCursor(ORIGIN_POS[0])
        tGame.render(HINT_COLOUR+"(ANY KEY) to continue"+Colour.RESET)
        tGame.renderCopy()
        self.key_in.keyIn()
        tGame.render("\033[2K")
        tGame.renderCopy()

    def expense_summary(self):
        tGame.screenClear()
        tGame.setCursor(ORIGIN_POS[0], ORIGIN_POS[1])
        tGame.render("Expense Summary\n"+'-'*30+'\n')

        if len(self.expenses_list) == 0: 
            tGame.render("You currently have no expenses to calculate.")
        else:
            total_expenses = 0
            for category, expenses in self.expenses_list.items():
                category_total = 0
                category_total = float(category_total)

                for expense in expenses:
                    category_total += expense['amt']

                total_expenses += category_total

                tGame.setCursor(ORIGIN_POS[0])
                tGame.render(f"Category - {category}: ${category_total}\n")

            tGame.render('\n')
            tGame.setCursor(ORIGIN_POS[0])
            tGame.render(f"Total: ${total_expenses}")

        tGame.render('\n\n')
        tGame.setCursor(ORIGIN_POS[0])
        tGame.render(HINT_COLOUR+"(ANY KEY) to continue"+Colour.RESET)
        tGame.renderCopy()
        self.key_in.keyIn()

    def add_expense(self):
        tGame.screenClear()

        ExpensesApp.help_display(40,2, "Input")

        tGame.setCursor(*ORIGIN_POS)
        y_pos = ORIGIN_POS[1]
        tGame.showCursor()

        tGame.render("What is the name of your expense?")

        y_pos +=1
        tGame.setCursor(ORIGIN_POS[0], y_pos)
        tGame.renderCopy()

        # Expense Name
        while True:
            name = tGame.textInput(self.key_in, ORIGIN_POS[0], y_pos)
            if name == CONTROLS.ESCAPE or name == KEY.QUIT:
                return

            if len(name.strip()) == 0:
                tGame.moveCursor('B', 1)
                tGame.setCursor(ORIGIN_POS[0])
                tGame.render(INVALID_COLOUR+"Invalid Input"+ Colour.RESET)

                # Reset to original position
                tGame.setCursor(ORIGIN_POS[0])
                tGame.moveCursor('A', 1)
                tGame.render("\033[2K")

                # Redraw Help which gets partially cleared by prev. line
                ExpensesApp.help_display(40,2, "Input")
                tGame.renderCopy()
            else:
                break

        # Category Name
        y_pos +=1
        tGame.setCursor(ORIGIN_POS[0], y_pos)
        # Extra space is quick and lazy way to overwrite line
        tGame.render("Category?           ")

        y_pos+=1
        tGame.setCursor(ORIGIN_POS[0], y_pos)
        tGame.renderCopy()
        while True:
            category = tGame.textInput(self.key_in, ORIGIN_POS[0], y_pos)

            if category == CONTROLS.ESCAPE or category == KEY.QUIT:
                return

            if len(category.strip()) == 0:
                tGame.moveCursor('B', 1)
                tGame.setCursor(ORIGIN_POS[0])
                tGame.render(INVALID_COLOUR+"Invalid Input"+ Colour.RESET)

                # Reset to original position
                tGame.setCursor(ORIGIN_POS[0])
                tGame.moveCursor('A', 1)
                tGame.render("\033[2K")

                # Redraw Help which gets partially cleared by prev. line
                ExpensesApp.help_display(40,2, "Input")
                tGame.renderCopy()
            else:
                break
        
        category = category.title().strip()

        y_pos += 1
        while True:
            tGame.setCursor(ORIGIN_POS[0], y_pos)
            tGame.render("How much is your expense?")

            tGame.setCursor(ORIGIN_POS[0], y_pos+1)
            tGame.renderCopy()

            amount = tGame.textInput(self.key_in,
                                     ORIGIN_POS[0], y_pos+1)

            if amount == CONTROLS.ESCAPE or name == KEY.QUIT:
                return

            amount = amount.strip(" $")
            try:
                amount = float(amount)
                amount = round(amount, 2)
                break
            except ValueError:
                tGame.moveCursor('B', 1)
                tGame.setCursor(ORIGIN_POS[0])
                tGame.render(INVALID_COLOUR+"Invalid Amount"+ Colour.RESET)

                # Reset to original position
                tGame.setCursor(ORIGIN_POS[0])
                tGame.moveCursor('A', 1)
                tGame.render("\033[2K")
                # Redraw Help which gets partially cleared by prev. line
                ExpensesApp.help_display(40,2, "Input")

                tGame.renderCopy()

        y_pos += 2
        date = self.input_date(ORIGIN_POS[0], y_pos)
        if date == KEY.QUIT: return

        expense = {
            "name": name,
            "amt": amount,
            "date": date
        }
        # Creates new key: category if doesn't already exist
        # Appends expense to the value (list) of key
        self.expenses_list.setdefault(category, []).append(expense)

    def input_date(self, x,y):
        today = time.strftime("%Y %m %d").split()
        
        tGame.setCursor(x,y)
        tGame.render("Leave blank for current date\n")

        # Year
        while True:
            tGame.setCursor(x,y+1)
            tGame.render("Year:")
            tGame.setCursor(x,y+2)
            tGame.render("\033[2K")
            tGame.renderCopy()
            year = tGame.textInput(self.key_in, x,y+2)
            
            if year == CONTROLS.ESCAPE or year == KEY.QUIT:
                return KEY.QUIT
            year = year.strip()
            if year.isdigit():
                year = int(year)
                break
            elif len(year) == 0:
                year = int(today[0])
                break

        # Month
        while True:
            tGame.setCursor(x,y+3)
            tGame.render("Month:")
            tGame.setCursor(x,y+4)
            tGame.render("\033[2K")
            tGame.renderCopy()
            month = tGame.textInput(self.key_in, x,y+4)

            if month == CONTROLS.ESCAPE or month == KEY.QUIT:
                return KEY.QUIT
            month = month.strip()
            if (month.isdigit() and 1<=int(month)<=12):
                # strips leading zero if inputted
                month = str(int(month))
                break
            elif month.lower() in MONTH_NAMES:
                month = str(MONTH_NAMES.index(month.lower())+1)
                break
            elif len(month) == 0:
                month = str(int(today[1]))
                break

        # Day
        while True:
            tGame.setCursor(x,y+5)
            tGame.render("Day:")
            tGame.setCursor(x,y+6)
            tGame.render("\033[2K")
            tGame.renderCopy()
            day = tGame.textInput(self.key_in, x,y+6)

            if day == CONTROLS.ESCAPE or day == KEY.QUIT:
                return KEY.QUIT
            
            day = day.strip()
            if len(day) == 0:
                day = today[2]
            if day.isdigit():
                day = int(day)
                if (month == '2' and day==29):
                    if (year % 4 == 0):
                        break
                    else:
                        continue
    
                elif (1<=day<=30 and month in "4 6 9 11".split()) or (
                      1<=day<=31 and month in "1 3 5 7 8 10 12".split()) or (
                      1<=day<=28 and month == '2'):
                    break
        return [year, int(month), day]      

    def remove_expense(self):
        # view expenses first
        self.view_expenses()

        # Clear screen and start remove_expense
        tGame.screenClear()
        tGame.setCursor(*ORIGIN_POS)
        tGame.showCursor()

        # Setup for UI
        tGame.render(Colour.FOREGROUND["RED"]+"Which one would you like to remove?"+Colour.RESET)         
        
        # Control Hint
        self.help_display(ORIGIN_POS[0]+35, ORIGIN_POS[1]+5, "Input")

        tGame.renderCopy()

        while True:          
            # Display categories
            tGame.setCursor(ORIGIN_POS[0],ORIGIN_POS[1]+4)
            tGame.render("Categories:\n")
            for category in self.expenses_list:
                tGame.setCursor(ORIGIN_POS[0]+2)
                # Constrains to 30 chars to prevent overflow into control display
                tGame.render(category[0:min(len(category), 30)] +
                             ("..." if len(category) >= 30 else "") +'\n')
            tGame.renderCopy()

            # Category Input
            tGame.setCursor(ORIGIN_POS[0],ORIGIN_POS[1]+1)
            tGame.render("\033[2K")
            tGame.render("Category:")

            
            tGame.renderCopy()
            category_choice = tGame.textInput(self.key_in,
                                     ORIGIN_POS[0]+10, ORIGIN_POS[1]+1)

            if category_choice == CONTROLS.ESCAPE or category_choice == KEY.QUIT:
                return

            category_choice = category_choice.strip().title()

            if category_choice not in self.expenses_list:
                tGame.setCursor(ORIGIN_POS[0], ORIGIN_POS[1]+2)
                tGame.render(INVALID_COLOUR+
                             "Invalid Option" + Colour.RESET)
                tGame.renderCopy()
                continue
            
            # Clear categories
            tGame.setCursor(ORIGIN_POS[0],ORIGIN_POS[1]+4)
            tGame.render("Expenses:  \n")
            for category in self.expenses_list:
                # End of string
                tGame.setCursor(ORIGIN_POS[0]+4+30)
                # Clear to beginning of line
                tGame.render("\033[1K\n")

            # Display expenses
            tGame.setCursor(1,ORIGIN_POS[1]+5)
            expense_num = 1
            for expense in self.expenses_list[category_choice]:
                expense = expense["name"]

                tGame.render(f"{expense_num}. ")
                # Constrains to 30 chars to prevent overflow into control display
                tGame.render(expense[0:min(len(expense), 30)] +
                             ("..." if len(expense) >= 30 else "") +'\n')
                expense_num += 1
            tGame.renderCopy()

            # Expense choice
            while True:
                # Clear "Invalid Option" tag if exists
                tGame.setCursor(ORIGIN_POS[0],ORIGIN_POS[1]+2)
                tGame.render("\033[2K")

                tGame.render("Expense #:")
                tGame.renderCopy()
    
                # Expense number
                choice = tGame.textInput(self.key_in,
                                         ORIGIN_POS[0]+11, ORIGIN_POS[1]+2)
    
                if choice == CONTROLS.ESCAPE or choice == KEY.QUIT:
                    return
    
                # Valid
                elif choice.strip().isdigit() and (
                        int(choice) in range (1,len(self.expenses_list[category_choice])+1)):
                    choice = int(choice)
                    self.expenses_list[category_choice].pop(choice-1)
                    if len(self.expenses_list[category_choice]) == 0:
                        del self.expenses_list[category_choice]
    
                    # Show remaining expenses
                    tGame.screenClear()
                    tGame.setCursor(*ORIGIN_POS)
                    tGame.render("Your remaining expenses are:")
                    tGame.renderCopy()
                    time.sleep(0.7)
                    self.view_expenses()

                    return
    
                # Invalid
                else:
                    tGame.setCursor(ORIGIN_POS[0], ORIGIN_POS[1]+3)
                    tGame.render(INVALID_COLOUR+
                                 "Invalid Option" + Colour.RESET)
                    tGame.renderCopy()

    def load_data(self):
        try:
            with open ("data.json", 'r') as f:
                self.expenses_list = json.loads(f.read())
        except FileNotFoundError:
            tGame.render("No save file found.\nCreating blank file...")
            tGame.renderCopy()

            self.expenses_list = {}
            self.save_data()

    def save_data(self):
        tGame.render("\nSaving...\n")
        tGame.renderCopy()
        with open ("data.json", 'w') as f:
            f.write(json.dumps(self.expenses_list))
        time.sleep(0.4)
        tGame.render("Done!\n")
        tGame.renderCopy()

    @staticmethod
    def help_display(x,y, option):
        if x<=0 or y<=0:
            raise ValueError(f"x and y must be integers above 0: found x:{x}, y:{y}")
        if option == "Main":
            start = 1
            height = 11
        elif option == "Input":
            start = 23
            height = 11

        tGame.setCursor(x=x,y=y)
        tGame.renderCopy()
        tGame.render(tGame.import_image("sprites.txt",height,start,do_colour=True).replace('\n','\033[1B\033['+str(x)+'G'))
        tGame.renderCopy()

if __name__ =="__main__":
    tGame.init()
    tGame.screenClear()
    tGame.setCursor(1,1)
    tGame.renderCopy()

    print("For best experience, please set terminal size to at least 70x35. Type 'y' to continue")
    while input("> ") != 'y':
        pass
    try:
        app = ExpensesApp()
        app.run()
    finally:
        tGame.end()

