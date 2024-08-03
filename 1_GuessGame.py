import random


print(f"Welcome to Guess Game\nYou have to guess the numbers correctly")

points = 0
game_over = False
while not game_over:
    rand_num = random.randrange(1,6)
    print(f"-"*30)
    player_guess = int(input(f"Choise number (1-5): "))
    if player_guess == rand_num:
        points += 1
        print(f"Wow your points now is {points}")
    else:
        print(f"You lost")
        game_over = True
        agine = input(f"do you want to play agine(y,n)?: ")
        if agine == "y":
            game_over = False