import random

def generate(games_count, code_count):
  codes  = []
  for i in range(1,games_count+1):
    random_numbers = random.sample(range(10000,99999), code_count)
    for randnum in random_numbers:
      code = f"Game-win-{randnum}"
      codes.append(code)
  
  return codes


print(generate(1,15))
