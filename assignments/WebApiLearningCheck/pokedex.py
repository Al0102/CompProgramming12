import requests
import os

def clear():
    os.system("cls" if os.name == 'posix' else "clear")

# drawing commands
newline8 = "\n\033[9G"
abs28 = "\033[27G"

CHOICES = ("Random Fact",
           "Find Pokemon by Pokedex #",
           "Find Pokemon by Name",
           "Browse",
           "Exit")

def inputPositiveInt(string):
    try:
        amount = input(string).strip()
        if not 0 < int(amount):
            raise ValueError()
    except ValueError:
        print("Invalid amount: "+amount)
        return -1

    return amount

def printPokeInfo(pokejson):
    clear()
    print("\033[1m"+
f"""

    Name:   {pokejson["name"].capitalize()}
    ID:     {pokejson["id"]}
    Types:  {' | '.join([ type["type"]["name"] for type in pokejson["types"] ])}
    Height: {pokejson["height"]/10}m
    Weight: {pokejson["weight"]/10}kg

    Base-Stats:
        {newline8.join([ f"{stat['stat']['name']}:{abs28}{stat['base_stat']}" for stat in pokejson['stats'] ])}

""" + "\033[0m"
    )

def main():
    clear()
    while True:
        for i in range(len(CHOICES)):
            print(f"{i+1}. {CHOICES[i]}")
    
        try:
            choice = int(input("> ").strip())
        except ValueError:
            print("\033[31mInvalid Choice\033[0m")
            continue

        print()
        match choice:
            # Fact
            case 1:
                while True:
                    amount = inputPositiveInt("Amount:\n> ")
                    if amount != -1:
                        break

                res = requests.get("https://pokefacts.vercel.app/?count="+amount)

                # If site is down or invalid get
                if res.status_code == 404:
                    print("Error reaching API")

                # Print Facts
                else:
                    for i in range(int(amount)):
                        print("\nFun Fact: "+res.json()["data"][i])
                    print()
            # Pokedex #
            case 2:
                while (number:=inputPositiveInt("Pokedex #:\n> ")) == -1: pass

                res =  requests.get("https://pokeapi.co/api/v2/pokemon/"+number)

                # If site is down or invalid get
                if res.status_code == 404:
                    print("Error reaching API or ID doesn't exist")
                # Print Pokemon info
                else:
                    printPokeInfo(res.json())
            # Name
            case 3:
                name = input("Pokemon Name:\n> ").strip().lower()

                res =  requests.get("https://pokeapi.co/api/v2/pokemon/"+name)

                # If site is down or invalid get
                if res.status_code == 404 or name.isdigit():
                    print("Error reaching API or Pokemon doesn't exist")
                # Print pokemon info
                else:
                    printPokeInfo(res.json())
            # Browse
            case 4:
                offset = 0
                AMOUNT = 10
                while True:
                    clear()
                    res =  requests.get(f"https://pokeapi.co/api/v2/pokemon?limit={AMOUNT}&offset={offset*AMOUNT}")
    
                    # If site is down or invalid get
                    if res.status_code == 404:
                        print("Error reaching API or Pokemon doesn't exist")

                    # Print list of pokemon
                    else:
                        id_ = offset*AMOUNT+1
                        for pokemon in res.json()["results"]:
                            print(f"{pokemon['name'].capitalize()} #{id_}")
                            id_ += 1
                    # Input
                    print("\nFor next page - '>'\nFor previous page - '<'\nTo go back to main menu - 'b'\n")
                    match input("> ").strip():
                        case '>':
                            offset += 1
                            # Exceeds max number of pokemon in database
                            if offset*AMOUNT>=1304:
                                offset -= 1
                        case '<':
                            offset = max(0, offset-1)
                        case 'b':
                            print()
                            break
            case 5:
                return
                        

if __name__ == "__main__":
    main()
