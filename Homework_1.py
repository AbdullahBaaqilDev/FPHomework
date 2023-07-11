import random

# defind colors
RED    = "\033[0;31m"
GREEN = "\033[0;32m"
WHITE = "\033[1;37m"
YELLOW = "\033[1;33m"
NONE   = "\033[0;0m"

print(f"{WHITE}Welcome to Guess Game\nYou have to guess the numbers correctly")

points = 0
game_over = False
while not game_over:
    rand_num = random.randrange(1,6)
    print(f"{NONE}-"*30)
    player_guess = int(input(f"{NONE}Choise number (1-5): {YELLOW}"))
    if player_guess == rand_num:
        points += 1
        print(f"{GREEN}Wow your points now is {points}")
    else:
        print(f"{RED}You lost{NONE}")
        game_over = True
        agine = input(f"do you want to play agine({YELLOW}y{NONE},{YELLOW}n{NONE})?: {YELLOW}")
        if agine == "y":
            game_over = False