# Zoo Database
def create_zoo():
    # Creates list of 5 inputs included in ["lion", "bear", "panda"]
    zoo_animals = [
                   input(f"Zoo Animal {i+1}: ").lower()
                       for i in range(5)
                  ]
    
    print('\n' + '_'*20 + '\n')
    print("Zoo:", end="\n    ")
    print(*zoo_animals, sep="\n    ", end="\n\n")
    
    # set() is to remove duplicates
    for animal in set(zoo_animals):
        amount = zoo_animals.count(animal)
        is_plural = amount!=1
        print(f"There {'are' if is_plural else 'is'} {amount} {animal}{'s' if is_plural else ''}")

# Colour Converter
def 
