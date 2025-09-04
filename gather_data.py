"""
This file was run to gather the data in the .csv file that will be used on the dashboard.
"""

from pybaseball import playerid_lookup, statcast_pitcher
import pandas as pd

# 18 most recent Cy Young winners, followed by 14 most recent runners up (which includes 2 older winners)
players_list = ["Tarik Skubal", "Chris Sale", "Gerrit Cole", "Blake Snell", "Justin Verlander", "Sandy Alcántara",
                "Robbie Ray", "Corbin Burnes", "Shane Bieber", "Trevor Bauer", "Jacob deGrom", "Corey Kluber",
                "Max Scherzer", "Rick Porcello", "Dallas Keuchel", "Jake Arrieta", "Clayton Kershaw", "David Price",
                "Seth Lugo", "Zack Wheeler", "Sonny Gray", "Logan Webb", "Dylan Cease", "Max Fried", "Kenta Maeda",
                "Yu Darvish", "Hyun Jin Ryu", "Jon Lester", "Zack Greinke", "Félix Hernández", "Johnny Cueto",
                "Adam Wainwright"]

all_player_stats = []

all_player_stats = []

for player_name in players_list:
    player_name_lst = player_name.split(" ")
    if player_name == "Hyun Jin Ryu": # Hyun Jin is the first name - need to manually correct splitting
        player_name_lst = ["Hyun Jin", "Ryu"]

    player_ids = playerid_lookup(player_name_lst[1], player_name_lst[0])
    
    mlbam_key = player_ids['key_mlbam'][0]

    player_stats = statcast_pitcher('2016-03-01', '2024-11-01', int(mlbam_key)) # Start in 2016 when statcast was everywhere, through end of 2024 playoffs
    player_stats = player_stats[player_stats['game_type'].isin(['R', 'P', 'F', 'D', 'L', 'W'])] # Filter out S (spring training) and E (exhibition)

    player_stats['pitch_type'] = player_stats['pitch_type'].replace('FA', 'FF') # Both codings mean four-seam fastball

    player_stats_sorted = player_stats.sort_values(
        by=['game_date', 'game_pk', 'at_bat_number', 'pitch_number']
    ).reset_index(drop=True) # Now in perfect chronological order (if we want this at some point)

    all_player_stats.append(player_stats_sorted)

all_player_stats_joined = pd.concat(all_player_stats, axis=0)

pitch_types = {
    'FF': 'Four-seam Fastball',
    'FT': 'Two-seam Fastball',
    'SI': 'Sinker',
    'FC': 'Cutter',
    'FS': 'Split-finger Fastball',
    'FO': 'Forkball',
    'SL': 'Slider',
    'CU': 'Curveball',
    'KC': 'Knuckle Curve',
    'CH': 'Changeup',
    'KN': 'Knuckleball',
    'EP': 'Eephus',
    'SC': 'Screwball',
    'GY': 'Gyroball',
    'SV': 'Sweeper',
    'ST': 'Slurve',
    'CS': 'Slow Curve',
    'PO': 'Pitchout',
    'IN': 'Intentional Ball',
    'UN': 'Unknown'
}

# Filter out eephus, pitchout, intentional ball, unknown, blank (irrelevant to a pitcher's arsenal)
all_player_stats_joined = all_player_stats_joined[~all_player_stats_joined['pitch_type'].isin(["EP", "PO", "IN", "UN", ""])]

# Change pitch_type from coding to name
all_player_stats_joined['pitch_type'] = all_player_stats_joined['pitch_type'].map(lambda code: pitch_types.get(code, code))

# Change player_name from Last, First to First Last
def change_name(name):
    last, first = name.split(", ")
    return f"{first} {last}"

all_player_stats_joined['player_name'] = all_player_stats_joined['player_name'].map(change_name)

# Also filter to just the columns we use in the dashboard - otherwise CSV is massive
all_player_stats_joined = all_player_stats_joined[['pitch_name', 'pitch_type', 'game_year', 'player_name', 'game_date', 'release_speed', 'balls', 'strikes', 'bb_type', 'events']].copy()

all_player_stats_joined.to_csv("all_pitchers_stats.csv")