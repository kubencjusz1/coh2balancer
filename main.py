from itertools import combinations
import PySimpleGUI as sg
import json
import random

#  Hardcoded data
FILE_NAME = 'cohstats'
MAPS = ["Huta w Essen", "Hill 400", "La Gleize", "Stepy", "Miasto 17", "Generał Gówno", "Redball", "Whiteball",
        "Las Lienne", "Atak na Lorch", "Nordwind", "Port w Hamburgu", "Road to Arnhem"]
POINTS_CONSTANT = 0.2
POINTS_PER_500 = 0.2
DIFF_AMORTIZATION = 0.1
MIN_GAINED_POINTS = 0.1
with open(FILE_NAME) as f:
    data = f.read()
    PLAYERS = json.loads(data)
PLAYERS_NAMES = sorted(list(PLAYERS.keys()))


# @@ Generowanie teamów @@
def team_generation(players: dict) -> (dict, dict, float):
    for player in players:
        players[player] = PLAYERS[player]
    group1, group2, diff = find_closest_combination(players)
    try:
        print("Group 1: ", {key: round(value, 2) for key, value in group1.items()})
        print("Group 2: ", {key: round(value, 2) for key, value in group2.items()})
        print("Różnica: ", 2*diff)
        print("\n", MAPS[random.randrange(len(MAPS))], "\n")
        if random.randrange(2)%2 == 0:
            print("Drużyna 1 Niemcy \nDrużyna 2 Alianci")
        else:
            print("Drużyna 1 Alianci \nDrużyna 2 Niemcy")
    except NameError:
        print("Groups not generated")
    return group1, group2, diff


def find_closest_combination(data: dict) -> (dict, dict, float):
    total_sum = sum(data.values())
    target_sum = total_sum / 2  # Żądana suma dla każdej grupy

    closest_sum_diff = float('inf')  # Najbliższa różnica pomiędzy sumami grup
    best_combination = None  # Najlepsza kombinacja grup

    for r in range(1, len(data)):
        for combination in combinations(data.keys(), r):
            group_sum = sum(data[key] for key in combination)
            diff = abs(target_sum - group_sum)

            if diff < closest_sum_diff:
                closest_sum_diff = diff
                best_combination = combination
                diff2 = target_sum - group_sum

    group1 = {key: data[key] for key in best_combination}
    group2 = {key: data[key] for key in data if key not in best_combination}

    return group1, group2, diff2


# @@ Kto wygrał @@
def update_results(group1: dict, group2: dict, number_of_winning_team: str, number_of_points: str):
    sum1 = sum(group1[key] for key in group1)
    sum2 = sum(group2[key] for key in group2)
    diff_not_absolute = sum1 - sum2
    team_number = int(number_of_winning_team)
    number_of_points = int(number_of_points)

    # Obliczanie ilorazu minimalnej i maksymalnej wartości
    quotient = min(PLAYERS.values()) / max(PLAYERS.values())

    # odejmujemy dla wygranego faworyta
    if diff_not_absolute > 0 and team_number == 1 or diff_not_absolute < 0 and team_number == 2:
        diff_not_absolute = -1 * abs(diff_not_absolute)
    else:
        diff_not_absolute = abs(diff_not_absolute)

    if team_number == 1:
        who_won_the_game(group1, diff_not_absolute, True, number_of_points, quotient)
        who_won_the_game(group2, diff_not_absolute, False, number_of_points, quotient)
    elif team_number == 2:
        who_won_the_game(group2, diff_not_absolute, True, number_of_points, quotient)
        who_won_the_game(group1, diff_not_absolute, False, number_of_points, quotient)
    print(f"\nDrużyna {team_number} wygrała i zyskała ranking\n")

    with open(FILE_NAME, 'w') as file:
        file.truncate(0)
        json.dump(PLAYERS, file)


def who_won_the_game(player_dict: dict, diff_not_absolute:float, win_loose: bool, number_of_points: int, quotient: float):
    common_keys = set(player_dict.keys()) & set(PLAYERS.keys())
    for key in common_keys:
        gained_points = calculate_points(diff_not_absolute, win_loose, number_of_points, quotient)
        PLAYERS[key] += gained_points


def calculate_points(diff_not_absolute: float, win_loose: bool, number_of_points: int, quotient: float) -> float:
    gained_points = (POINTS_CONSTANT + POINTS_PER_500 * (number_of_points / 500) + DIFF_AMORTIZATION * diff_not_absolute) *quotient
    if not win_loose:
        gained_points = -1*gained_points
    return max(gained_points, MIN_GAINED_POINTS) if win_loose else min(gained_points, -MIN_GAINED_POINTS)


# @@ Generowanie UI @@
layout = [
    [sg.Text('Git Gud')],
    [sg.Button('Odśwież')],
    [sg.Combo(PLAYERS_NAMES, size=(12,20)), sg.Combo(PLAYERS_NAMES, size=(12,20)), sg.Combo(PLAYERS_NAMES, size=(12,20)), sg.Combo(PLAYERS_NAMES, size=(12,20))],
    [sg.Combo(PLAYERS_NAMES, size=(12,20)), sg.Combo(PLAYERS_NAMES, size=(12,20)), sg.Combo(PLAYERS_NAMES, size=(12,20)), sg.Combo(PLAYERS_NAMES, size=(12,20))],
    [sg.Button('Generuj paringi')],
    [sg.Text('Kto wygrał rundę'), sg.Text(''), sg.Text('Ile punktów miał zwycięzca')],
    [sg.Combo(['1', '2']), sg.Text('                  '), sg.Input(size=(5,2))],
    [sg.Button('Potwierdź wygraną')],
    [sg.Output(size=(110,20))]
]
window = sg.Window('CoH2 custom balancer by Kubencjusz', layout)


while True:  # Pentla eventów i inputów
    event, values = window.read()
    if event == 'Odśwież':
        with open(FILE_NAME) as f:
            data = f.read()
            PLAYERS = json.loads(data)
        PLAYERS_NAMES = sorted(list(PLAYERS.keys()))

    if event == 'Generuj paringi':
        try:
            players = {value: key for key, value in values.items()}
            players = dict(list(players.items())[:8])
            group1, group2, diff = team_generation(players)
        except KeyError:
            print("Najpierw wybierz graczy!/ Jesten z graczy jest źle dodany!")
    if event == 'Potwierdź wygraną':
        try:
            update_results(group1, group2, values[8], values[9])
        except NameError:
            print("Najpierw mecz zagraj pajacu!")
    if event == sg.WIN_CLOSED:  # killer
        break
window.close()
