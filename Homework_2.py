import random

# defind colors
RED    = "\033[0;31m"
GREEN = "\033[0;32m"
WHITE = "\033[1;37m"
YELLOW = "\033[1;33m"


def start_game():# def تشير الى دالة والتي تقوم بمهام معينة حين مناداتها، ومناداتها تكون بكتابة اسمها بجانب الاقوس بدون كلمة ديف

    print(f"{WHITE}_"*40)
    # طلب المعلومات من المستخدم
    players_number = int(input(f"{WHITE}Enter player number:-{YELLOW} "))
    attempts = int(input(f"{WHITE}Enter attempts number:-{YELLOW} "))
    print(f"{WHITE}-"*40)
    players_names = []# الاقواس المربعة تشير الى مصفوفة تحتوي مجموعة من القيم
    players_scores = []

    for player_index in range(players_number):# for هو عبارة عن تكرار لأوامر معينة
        player_name = input(f"{WHITE}Player {player_index + 1} enter your name:-{YELLOW} ")
        players_names.append(player_name)# append تستعمل لاضافة قيمة معينة الى المصفوفة
        print(f"{WHITE}-"*30)

    for player in range(players_number):# range(start,stop,steps)
        score = 0
        print(f"{GREEN}{players_names[player]} you can start:{WHITE}")
        for attempt in range(attempts):
            random_number = random.randrange(1,6)
            player_guess = int(input(f"{WHITE}Guess a number (1,5):-{YELLOW} "))
            if player_guess == random_number:
                score += 1
                print(f"{GREEN}WOOOW you got it{WHITE}")
            else:
                print(f"{RED}Sorry the number was {random_number}{WHITE}")
        players_scores.append(score)
        print(f"{WHITE}-"*30)

    print_scores(
        players_names = players_names,
        players_scores = players_scores,
        function = start_game
        )# منادات دالة print_scores()
    
def print_scores(players_names,players_scores,function):
    for player in range(len(players_names)):# len تستعمل لاجاد طول مصفوفة على عدد القيم الموجودة
        print(f"{GREEN}{players_names[player]} score is {players_scores[player]}")
    max_score = max(players_scores)# max ترجع باقيمة الاكبر
    print(f"{GREEN}Winners:{WHITE}")
    for index,score in enumerate(players_scores):
        if score == max_score and max_score != 0:
            print(f"{GREEN}{players_names[index]}{WHITE}")
    agine(function)

def agine(function):
    play_agine = input("Do you want to play agine (y,n)? ")
    if play_agine == "y":
        function()
    else:
        exit()

start_game()