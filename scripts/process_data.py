import re
import string

import numpy as np
import pandas as pd
import os
from pathlib import Path
import math

mapping = {
    "" : 1,
    "a": 2,
    "b": 3,
    "c": 4,
    "d": 5,
    "e": 6,
}

startbahn_mapping_heim = {
    "1": 1,
    "2": 3,
    "3": 1,
    "4": 3,
    "5": 1,
    "6": 3,
}

startbahn_mapping_gast = {
    "1": 2,
    "2": 4,
    "3": 2,
    "4": 4,
    "5": 2,
    "6": 4,
}

data_dir = Path('alte_daten')

all_data = pd.DataFrame()

for filename in os.listdir(data_dir):
    data = pd.read_csv(data_dir / filename, sep=',')
    print(f"Processing file: {filename}, shape: {data.shape}")
    
    all_samples = []

    # iterate over all rows in the dataframe
    for index, row in data.iterrows():
        # search for all columns matching the pattern "auf_(.*)pass" in the row
        player_columns = [col for col in row.index if col.startswith("auf_") and col.endswith("pass")]
        for player_column in player_columns:
            
            # get text between "auf_" and "pass" in the column name
            player_index = re.search(r"auf_(.*)pass", player_column).group(1)
            
            if "ers" in player_index:
                continue
            
            # check if g is in the player_index, if so, it's a guest player, otherwise it's a home player
            if "g" in player_index:
                letter = player_index.replace("g", "")
                number = mapping[letter]
                home = False
                
                mp = 4 - row[f"map{number}"]
                sp = row[f"{letter}spkteins"] + row[f"{letter}spktzwei"] + row[f"{letter}spktdrei"] + row[f"{letter}spktvier"]
                startbahn = startbahn_mapping_gast[str(number)]
            else:
                number = mapping[player_index]
                home = True
                
                mp = row[f"map{number}"]
                sp = row[f"{player_index}spkteins"] + row[f"{player_index}spktzwei"] + row[f"{player_index}spktdrei"] + row[f"{player_index}spktvier"]
                startbahn = startbahn_mapping_heim[str(number)]
                
            # create a new sample with the relevant fields
            sample = {
                "uhrzeit": row["uhrzeit"],
                "datum": row["datum"],
                "round": row["round"],
                "bahn": str(row["bahn"]) + " " + str(row["ort"]),
                "liga": row["liga"],
                "geschlecht": "w" if row["damen"] == 1 else "m",
                "passnummer": int(row[player_column]) if not pd.isnull(row[player_column]) else None,
                "name": row[f"auf_{player_index}name"],
                "gesamt": row[f"{player_index}dg{number}gesamt"],
                "bahn1": row[f"{player_index}dgeins"],
                "bahn2": row[f"{player_index}dgzwei"],
                "bahn3": row[f"{player_index}dgdrei"],
                "bahn4": row[f"{player_index}dgvier"],
                "dg": math.ceil(number/2),
                "heim": home,
                "mp": mp,
                "sp": sp,
                "startbahn": startbahn
            }
            all_samples.append(sample)
            
    # convert to a pandas dataframe
    all_samples_df = pd.DataFrame(all_samples)

    # column passnummer should be of type int
    all_samples_df['passnummer'] = all_samples_df['passnummer'].astype('Int64')
    all_samples_df['gesamt'] = all_samples_df['gesamt'].astype('Int64')
    all_samples_df['bahn1'] = all_samples_df['bahn1'].astype('Int64')
    all_samples_df['bahn2'] = all_samples_df['bahn2'].astype('Int64')
    all_samples_df['bahn3'] = all_samples_df['bahn3'].astype('Int64')
    all_samples_df['bahn4'] = all_samples_df['bahn4'].astype('Int64')

    # if name is null, try to get it by looking if there is another player with the same passnummer, and get the name from that player
    for index, row in all_samples_df[all_samples_df['name'].isnull()].iterrows():
        if not pd.isnull(row['passnummer']):
            name = all_samples_df[all_samples_df['passnummer'] == row['passnummer']]['name'].dropna().unique()
            if len(name) > 0:
                all_samples_df.at[index, 'name'] = name[0]
                
    # concatenate all_samples_df to all_data
    all_data = pd.concat([all_data, all_samples_df], ignore_index=True)

# save the dataframe to a csv file
all_data.to_csv('data_2013_2019.csv', index=False)