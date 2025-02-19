import random
import os
import time

# Tuple of my selected ASCII images
ascii_art = [
    ("penguin", """
   _~_
  (o o)
 /  V  \\ 
 /(___)\ 
^^~~~~~^^
"""),
    ("boat", """
             /|~~~   
           ///|      
         /////|      
       ///////|      
     /////////|      
   \==========|===/  
~~~~~~~~~~~~~~~~~~~~~    "      `
"""),
    ("car", """
  ______
 /|_||_\\`.__
(   _    _ _\\
=`-(_)--(_)-'
"""),
    ("house", """
   _______
  /       \\
 /_________\\
 |         |
 |  _   _  |
 | |_| |_| |
 |         |
 |_________|
"""),
    ("tree", """
   /\\
  /  \\
 /____\\
   ||
   ||
"""),
    ("snowman", """
   _|==|_  
    ('')___/
>--(`^^')
  (`^'^'`)
  `======'  ldb
 """)
]

def clear():
    # Clear console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def guessing_game():
    random.shuffle(ascii_art)
    total_score = 0
    # Shuffle ASCII images and set initial score to 0

    for name, art in ascii_art:
        start_time = time.time()  # Start time
        print(art)  # Display the ASCII art
        guess = input("Can you guess what this ASCII art represents? \nYour answer: ").strip().lower()
        attempts = 1  # Initialize attempts (start)

        while guess != name.lower():
            clear()
            print(art)  # Redisplay the ASCII art
            guess = input("Incorrect! Try again: ").strip().lower()
            attempts += 1  # Increment attempts (each attempt)

        end_time = time.time()
        time_taken = end_time - start_time  # Calculate time taken
        clear()
        print(f"Correct! It is a {name}.")
        print(f"It took you {attempts} {'attempt' if attempts == 1 else 'attempts'} and {time_taken:.2f} seconds to guess correctly.\n")
        total_score += attempts + time_taken  # Update total score

    # Display total score
    print(f"Game Over! Your total score is {total_score:.2f} (lower score is better, score is based on total attempts + total time taken)!")

# Run the game in the define function
guessing_game()
