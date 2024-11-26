import random
import string

def generate(games_count, code_count):
    codes = set()  # Use a set to keep track of unique codes

    for i in range(1, games_count + 1):
        randnums = random.sample(range(10000, 99999), code_count)  # Ensure unique random numbers within each game

        for randnum in randnums:
            rand_chars = ''.join(random.choices(string.ascii_uppercase, k=2))
            code = f"Game{i}-{randnum}{rand_chars}"
            
            # Ensure the code is unique by checking if it's already in the set
            while code in codes:
                rand_chars = ''.join(random.choices(string.ascii_uppercase, k=2))  # Regenerate random characters
                code = f"Game{i}-{randnum}{rand_chars}"

            codes.add(code)  # Add the unique code to the set
    
    return sorted(list(codes))

def generatewin(code_count):
    codes = set()
    randnums = random.sample(range(10000, 99999), code_count)  # Ensure unique random numbers within each game

    for randnum in randnums:
        rand_chars = ''.join(random.choices(string.ascii_uppercase, k=2))
        code = f"Game-win-{randnum}{rand_chars}"
        
        # Ensure the code is unique by checking if it's already in the set
        while code in codes:
            rand_chars = ''.join(random.choices(string.ascii_uppercase, k=2))  # Regenerate random characters
            code = f"Game-win-{randnum}{rand_chars}"

        codes.add(code) 

    return sorted(list(codes))


print(generatewin( 20))
  





