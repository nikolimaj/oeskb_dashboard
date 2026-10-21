from datetime import datetime
import pandas as pd
import requests

base_url = "https://firestore.googleapis.com/v1/projects/oeskb-app/databases/(default)/documents/saisonen/"

current_year = datetime.now().year
current_month = datetime.now().month
season = f"{current_year}_{current_year+1}"

if current_month <= 7:
    suffix = "F"
else:
    suffix = "H"

leagues  = {
    "SL Damen": "1_8_",
    "BL Damen": "1_7_",
    "SL Herren": "1_6_",
    "BL Herren Ost": "1_5_",
    "BL Herren West": "1_4_",
}
        
def get_games_data(games_url):
    response = requests.get(games_url)
    data = response.json()

    games = data['fields']['spiele']['mapValue']['fields']
    game_keys = list(games.keys())

    game_data = pd.DataFrame()

    for game_key in game_keys:
        game = games[game_key]["mapValue"]["fields"]["infos"]["mapValue"]["fields"]
        game_series = pd.json_normalize(game)
        game_series['spiel_id'] = game_key
        game_data = pd.concat([game_data, game_series], ignore_index=True)

    game_data = game_data.rename(columns={
        'datum.stringValue': 'datum',
        'uhrzeit.stringValue': 'uhrzeit',
        'bahn.stringValue': 'bahn',
    })

    game_data = game_data[["datum", "uhrzeit", "bahn", "spiel_id"]]

    return game_data

def get_results_and_player_data(results_url):
    response = requests.get(results_url)
    data_results = response.json()

    results = data_results['fields']['spiele']['mapValue']['fields']
    game_keys = list(results.keys())

    result_data = pd.DataFrame()
    for game in game_keys:
        for location in ['heim', 'gast']:

            players = results[game]['mapValue']['fields'][location]['mapValue']['fields']['spieler']['mapValue']['fields']
            player_keys = list(players.keys())

            for player_key in player_keys:
                player = players[player_key]['mapValue']['fields']
                player_series = pd.json_normalize(player)
                player_series['spieler_id'] = player_key
                player_series['heim'] = location == 'heim'
                player_series['spiel_id'] = game
                result_data = pd.concat([result_data, player_series], ignore_index=True)

    # if integer value is not set, take double value
    result_data['sp'] = result_data['sp.integerValue'].fillna(result_data['sp.doubleValue'])

    if 'mp.doubleValue' in result_data.columns:
        result_data['mp'] = result_data['mp.doubleValue'].fillna(result_data['mp.integerValue'])
    else:
        result_data['mp'] = result_data['mp.integerValue']

    results = result_data[["spieler_id", "spiel_id", "kegel.integerValue", "sp", "mp", "heim", "bahn.integerValue", "dg.integerValue"]]
    results = results.rename(columns={
        'kegel.integerValue': 'kegel',
        'bahn.integerValue': 'startbahn',
        'dg.integerValue': 'dg',
    })


    player_data = result_data.drop_duplicates(subset=['spieler_id'])

    player_data = player_data.rename(columns={
        'land.stringValue': 'land',
        'name.stringValue': 'name',
        'akJahr.integerValue': 'jahrgang',
    })

    player_data = player_data[["spieler_id", "name", "jahrgang", "land"]]
    player_data[['passnummer', 'name']] = player_data['name'].str.split(' / ', n=1, expand=True)
    
    
    return results, player_data




all_games = pd.DataFrame()
all_players = pd.DataFrame()

for league, id in leagues.items():
    games_url = base_url + id + season
    results_url = games_url + "/schnittliste/" + id + season + suffix
    
    print(f"Processing {season} - {league}")

    # Get game data
    try:
        game_data = get_games_data(games_url)
        game_data['liga'] = league
        
        # Get results data
        results, player = get_results_and_player_data(results_url)

        player = player.drop_duplicates(subset=['spieler_id'])

        if "Damen" in league:
            player['geschlecht'] = 'w'
        else:
            player['geschlecht'] = 'm'

        # concat game data with results
        game_data = pd.merge(results, game_data , on='spiel_id', how='left')

        all_games = pd.concat([all_games, game_data], ignore_index=True)
        all_players = pd.concat([all_players, player], ignore_index=True)
    
    except Exception as e:
        print(f"Error processing {season} - {league}: {e}")

all_players = all_players.drop_duplicates()

# join games and players data
player_games = pd.merge(all_games, all_players, on='spieler_id', how='left')

# drop duplicates
player_games = player_games.drop_duplicates(subset=['spieler_id', 'spiel_id'])


# append previous season data to current season data
previous_season = pd.read_csv("parsed_data/game_data_previous.csv")
player_games = pd.concat([previous_season, player_games], ignore_index=True)

player_games.to_csv("parsed_data/game_data_latest.csv", index=False)