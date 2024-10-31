# Pyramid
def pyramid():
    # Clears screen
    print("\033[2J\033[;H")

    # Takes advantage of list comprehension to one line multiple for loops
    # prints ' ' for the index of the current layer (e.g 0, 1, 2 - ''. ' ', '  '),
    # then '#' for the total amount (n) - 2 for each layer up (taking off one from the left and right of the pyramid)
    n = int(input()); [print(" "*(i) + '#'*(n-(i*2))) for i in range(n-n//2-1, -1, -1)] if n >=0 else [print(' '*(i) + '#'*(abs(n)-i*2)) for i in range(abs(n)-abs(n)//2)]

# ATM
def ATM():
    # Clear screen
    print("\033[2J\033[;H")

    # first iteration of for loop is sign up and login
    # second is withdrawal and deposit if login successful
    for x, y in [([1], [1]), ([0], [0])]: [ [ (balance:=100000), print(f"Balance: {balance}\nWithdraw | Deposit | Quit"), [[x.append(0), [(amount_change:=input("Amount: ")), (amount_change:=abs(int(amount_change)) if amount_change.isnumeric() else 0),(balance:=balance+(amount_change if input_ == "deposit" else -amount_change)), print(f"Balance: {balance}\nWithdraw | Deposit | Quit")] if input_ in ("withdraw", "deposit") else print("Not an Option")] if ( (input_:=input().lower()) and input_ != "quit" ) else print("Logging out...") for _ in x]] if login_success else print("Bye Bye")] if x[0] == 0 else [print("Set pin:"), [print(str([x.append(1)][0])+"\033[1000Dplease enter a 4-digit, positive integer") if (not (len(n:=input())==4 and n.replace('-','x').replace('(','x').isnumeric())) else [print("Login:"), [[print(str(x.pop())+"\033[1000DWelcome"), (login_success:=True)] if (n==(input())) else [print(str([y.append(1) if len(y) < 3 else print("\033[1Btoo many attempts\033[2A")][0])+"\033[2K\033[1000Dincorrect", end='\n\n'), (login_success:=False)] for i in y]] for j in x]]

def main():
    while True:
        input_ = input("Pyramid, ATM or quit: ").lower()
        if len(input_) <= 0:
            continue
        if input_[0] == "p":
            pyramid()
        elif input_[0] == "a":
            ATM()
        elif input_[0] == "q":
            return
        else:
            print("Not an option buddy")

if __name__ == "__main__":
    main()
