import requests
from bs4 import BeautifulSoup
import pandas as pd

# Default dict that will be used to store everything
predicts = {}

# Simple class just to simplify
class Game:
    def __init__(self):
        self.name = ''
        self.predict = ''

# Running every function that we have for scraping the predicts from each website
# To add more websites, you will need to add the function name on the function array
def main():
    functions = [forebet, predictz, windrawwin, soccervista]
    for func in functions:
        func()

def forebet():
    global predicts
    # https://www.forebet.com/en/football-tips-and-predictions-for-today
    
    predicts['forebet'] = []

    url = "https://www.forebet.com/en/football-tips-and-predictions-for-today"
    page = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"})

    soup = BeautifulSoup(page.content, "html.parser")
    games = soup.find_all(class_="rcnt tr_1")

    for game in games:
        name = game.find("meta", {"itemprop":"name"})

        if name is None: 
            continue

        game_class = Game()
        game_class.name = name.attrs['content']
        game_class.predict = game.find('span', {"class": "forepr"}).text

        predicts['forebet'].append({'game': game_class.name, 'predict': game_class.predict})

def predictz():
    global predicts
    # https://www.predictz.com/predictions

    predicts['predictz'] = []

    url = "https://www.predictz.com/predictions"
    page = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"})

    soup = BeautifulSoup(page.content, "html.parser")
    games = soup.find_all(class_='ptcnt')

    for game in games:
        home = game.find("div", {"class": "ptmobh"}).text
        away = game.find("div", {"class": "ptmoba"}).text

        if home == '' or away == '':
            continue

        game_class = Game()
        game_class.name = home + " vs " + away

        predict_text = game.find("div", {"class": "ptpredboxsml"}).text
        game_class.predict = '1' if 'Home' in predict_text else '2' if 'Away' in predict_text else 'X'

        predicts['predictz'].append({'game': game_class.name, 'predict': game_class.predict})

def windrawwin():
    global predicts
    # https://www.windrawwin.com/predictions/today

    predicts['windrawwin'] = []

    url = "https://www.windrawwin.com/predictions/today"
    page = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"})

    soup = BeautifulSoup(page.content, "html.parser")
    games = soup.find_all(class_='wttr')

    for game in games:
        game_name = game.find("span", {"class": "wtmoblnk"}).text

        if ' v ' not in game_name:
            continue

        game_class = Game()
        game_class.name = game_name.split(' v ')[0] + " vs " + game_name.split(' v ')[1]
        predict_text = game.find("div", {"class": "wtprd"}).text # Home 2-0
        game_class.predict = '1' if 'Home' in predict_text else '2' if 'Away' in predict_text else 'X'

        predicts['windrawwin'].append({'game': game_class.name, 'predict': game_class.predict})

def soccervista():
    global predicts
    # https://www.newsoccervista.com/

    predicts['soccervista'] = []

    url = "https://www.newsoccervista.com"
    page = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"})

    soup = BeautifulSoup(page.content, "html.parser")
    games = soup.find_all(class_='twom')

    for game in games:
        home = game.find("div", {"class": "hometeam"}).text
        away = game.find("div", {"class": "awayteam"}).text

        if home == '' or away == '':
            continue

        game_class = Game()
        game_class.name = home + " vs " + away
        game_class.predict = game.find("strong").text

        predicts['soccervista'].append({'game': game_class.name, 'predict': game_class.predict})

main()

# Storing all the array names to filter the games and the predicts
to_filter = list(predicts.keys())

# Creating an empty array to store all the games from every website
predicts['games'] = ['']

# Group all the games from every website and tried to ignore existing ones
for arr in to_filter:
    for to_add_games in predicts[arr]:
        found = False
        for game in predicts['games']:
            game_teams = to_add_games['game'].split(' vs ')

            home_name = game_teams[0]
            away_name = game_teams[1]

            if home_name in game or away_name in game:
                found = True
        if found == False:
            predicts['games'].append(to_add_games['game'])

# Match the predicts with the games from the websites
for arr in to_filter:
    predicts['predicts_' + arr] = []
    for game in predicts['games']:
        found = False
        for game_to_filter in predicts[arr]:
            game_teams = game_to_filter['game'].split(' vs ')

            home_name = game_teams[0]
            away_name = game_teams[1]

            if home_name in game or away_name in game:
                predicts['predicts_' + arr].append(game_to_filter['predict'])
                found = True
                break

        if found == False:
            predicts['predicts_' + arr].append('')

# Creating the xlsx with the games and the predicts of every website and for each game
df = pd.DataFrame({
    'Games': predicts['games'], 
    'Forebet': predicts['predicts_forebet'], 
    'PredictZ': predicts['predicts_predictz'], 
    'WinDrawWin': predicts['predicts_windrawwin'], 
    'SoccerVista': predicts['predicts_soccervista']
})

writer = pd.ExcelWriter('predicts.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Predicts')

# Simple stylings
writer.sheets['Predicts'].set_column('B:B', 50)
writer.sheets['Predicts'].set_column('E:E', 15)

writer.save()