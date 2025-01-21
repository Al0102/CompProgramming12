import random


# Rolls a six-sided die
def roll_die():
    result = random.randint(1, 6)  # Generate a random number between 1 and 6

    return result


# Simulates rolling the die multiple times
def roll_multiple_dice(num_rolls):
    rolls = []

    for _ in range(num_rolls):
        roll = roll_die()
        rolls.append(roll)

    return rolls


# Main function to prompt the user for the number of rolls and display the result
def main():
    print("Welcome to the Dice Roller!")

    num_rolls = int(input("How many times would you like to roll the die? "))

    rolls = roll_multiple_dice(num_rolls)

    print('_'*10 + '\n') # Spacing
    print("Results of the dice rolls:")
    for roll in rolls:
        print(roll)
    print('_'*10 + '\n') # Spacing


# Call the main function to run the program
if __name__ == "__main__":
    main()
