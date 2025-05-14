import random
import csv
from app import app, db
from app.models import Hero, Medal, Map, GameMode
import math

# each time it will half (for even num of teams)
def games_per_round(num_teams):
    n_games = [num_teams // (2 ** (i + 1)) for i in range(int(math.log2(num_teams)))]
    return n_games

# Function to generate a random CSV file in the specified format
def generate_csv(file_path, heroes, medals, maps, modes, num_teams):

    if num_teams <= 0:
        raise ValueError("num_teams must be a positive integer")
    if not (num_teams & (num_teams - 1)) == 0:
        raise ValueError("num_teams must be a power of 2")

    num_rounds = math.log2(num_teams)
    num_games = num_teams - 1

    call_count = 0
    def get_round():
        nonlocal call_count
        call_count += 1
        remaining = call_count
        for round_number, games in enumerate(games_per_round(num_teams), start=1):
            if remaining <= games:
                return round_number
            remaining -= games
        return None

    def random_name(prefix='', k=8):
        return prefix + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', k=k))

    def random_stat(min_val, max_val):
        return random.randint(min_val, max_val)

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)


        # Generate game header
        teams = [f"Team{i+1}" for i in range(num_teams)]
        # Initialize fixed teams and assign 6 players to each
        players_by_team = {team: [f"{team}_Player{j+1}" for j in range(6)] for team in teams}
        
        
        # Simulate elimination bracket (single-elimination)
        round_teams = teams.copy()
        round_number = 1

        while len(round_teams) > 1:
            next_round_teams = []

            # Pair up teams for current round
            for i in range(0, len(round_teams), 2):
                team_a = round_teams[i]
                team_b = round_teams[i+1]
                winning_team = random.choice([team_a, team_b])
                game_mode = random.choice(modes)
                game_map = random.choice(maps)

                writer.writerow(['', team_a, team_b, winning_team, game_mode, game_map, round_number, '', '', ''])

                team_a_players = players_by_team[team_a]
                team_b_players = players_by_team[team_b]
                all_players = team_a_players + team_b_players

                heroes_shuffled = heroes.copy()
                random.shuffle(heroes_shuffled)
                # Assign MVP and SVP (from different teams)
                mvp = random.choice(team_a_players)
                svp_candidates = [p for p in team_b_players if p != mvp]
                svp = random.choice(svp_candidates) if svp_candidates else random.choice(team_b_players)
                writer.writerow(['', "MVP", mvp, '', '', '', '', '', '', ''])
                writer.writerow(['', "SVP", svp, '', '', '', '', '', '', ''])

                medals_remaining = [m for m in medals if m not in ["MVP", "SVP"]]
                random.shuffle(medals_remaining)
                for medal in medals_remaining:
                    writer.writerow(['', medal, random.choice(all_players), '', '', '', '', '', '', ''])

                for player_name in all_players:
                    kills = random_stat(0, 30)
                    deaths = random_stat(0, 30)
                    assists = random_stat(0, 30)
                    final_hits = random_stat(0, 30)
                    damage = random_stat(1000, 10000)
                    damage_blocked = random_stat(0, 10000)
                    healing = random_stat(0, 10000)
                    accuracy = random_stat(0, 100)
                    hero = heroes_shuffled.pop()

                    writer.writerow([
                        player_name, kills, deaths, assists, final_hits, damage,
                        damage_blocked, healing, accuracy, hero
                    ])

                next_round_teams.append(winning_team)

            round_teams = next_round_teams
            round_number += 1


def fetch_heroes():
    return [hero.hero_name for hero in db.session.query(Hero).all()]

def fetch_medals():
    # TODO: actually store this in the db and then read from it
    # True false values refer to if it is unique (given to one player only)
    return [
        "MVP",
        "SVP",
        "3 Medal",
        "4 Medal",
        "5 Medal",
        "Fire Medal",
        "Sword Medal",
        "Shield Medal",
        "Plus Medal",
        "Fist Medal"
    ]

def fetch_maps():
    return [game_map.map_name for game_map in db.session.query(Map).all()]

def fetch_modes():
    return [game_mode.game_mode_name for game_mode in db.session.query(GameMode).all()]


if __name__ == "__main__":
    with app.app_context():
        heroes = fetch_heroes()
        medals = fetch_medals()
        maps = fetch_maps()
        modes = fetch_modes()
        
        # YOU CAN CHANGE THE NUMBER OF TEAMS TO ANY POWER OF 2, WHICH DETERMINES
        # THE NUMBER OF ROUNDS AND GAMES
        generate_csv("app/testing/generated_game.csv", heroes, medals, maps, modes, 
                     num_teams=8)