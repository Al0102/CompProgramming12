def convert(a): return a.replace(":)", "😊").replace(":(", "😢") 
print(input("To lowercase: ").lower() + "\n" + input("Give attitude: ").replace(" ", "...") + "\n" + convert(input("Emotify: ")) + "\n" + str(int(input("Relative energy of this mass: ")) * (3*10**8)**2) )
