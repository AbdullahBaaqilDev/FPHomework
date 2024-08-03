import random


def start_game():

    print(f"_"*40)
    
    players_number = int(input(f"Enter player number:- "))
    attempts = int(input(f"Enter attempts number:- "))
    print(f"-"*40)
    players_names = []
    players_scores = []

    index = 0
    while index < players_number:
        player_name = input(f"Player {index + 1} enter your name:- ")
        players_names.append(player_name)
        print(f"-"*30)
        index += 1

    number = 0
    while number < players_number:
        score = 0
        print(f"{players_names[number]} you can start:")
        attempt = 0
        while attempt < attempts:
            random_number = random.randrange(1,6)
            player_guess = int(input(f"Guess a number (1,5):- "))
            if player_guess == random_number:
                score += 1
                print(f"WOOOW you got it")
            else:
                print(f"Sorry the number was {random_number}")
            attempt += 1
        players_scores.append(score)
        print(f"-"*30)
        number += 1

    print_scores(
        players_names = players_names,
        players_scores = players_scores,
        function = start_game
        )
    
def print_scores(players_names,players_scores,function):
    name_number = 0
    while name_number < len(players_names):
        print(f"{players_names[name_number]} score is {players_scores[name_number]}")
        name_number += 1
    max_score = max(players_scores)
    print(f"Winners:")
    for index,score in enumerate(players_scores):
        if score == max_score and max_score != 0:
            print(f"{players_names[index]}")
    agine(function)

def agine(function):
    play_agine = input("Do you want to play agine (y,n)? ")
    if play_agine == "y":
        function()
    else:
        exit()

start_game()