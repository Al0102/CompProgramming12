def print_growing_pyramid(height):
    # Loop through each level of the pyramid
    for i in range(1, height + 1):
        # Step 1: Calculate the spaces before the hashes to center the pyramid
        spaces = ' ' * (height - i)  # Subtract the current level number from the height to center
        # Step 2: Calculate the number of `#` characters for the current level
        notes = '#' * (2 * i - 1)  # Number of hashes is odd, 1, 3, 5, 7, 9, ...
        # Step 3: Combine spaces and hashes to form the current row
        row = spaces + notes
        # Step 4: Print the row (this shows the growing pyramid visually)
        print(row)
        # Additional note: show what the spaces and hashes look like at this step
#        print(f"Level {i}: Spaces = '{spaces}', Notes = '{notes}'")

# Step 5: Ask the user for the height of the pyramid
while True:
    try:
        # Get user input for the height
        height = int(input("Enter the height (positive integer)!: "))
        if height <= 0:
            print("Please enter positive integer bigger than 0!")
        else:
            break  # Exit loop if input is valid
    except ValueError:
        print(" Please enter positive integer!")

# Step 6: Call the function to print the pyramid based on user input
print_growing_pyramid(height)
