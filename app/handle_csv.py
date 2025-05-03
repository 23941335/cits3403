import pandas as pd

TEAM_SIZE = 6

def try_convert_int(value):
    try:
        return int(value)
    except:
        return value

class CSV_Game():
    def __init__(self):
        self.team_a = None
        self.team_b = None
        self.winner = None
        self.game_mode = None
        self.map = None
        self.medals = []
        self.team_a_players = []
        self.team_b_players = []

    def process_header_row(self, header_row):
        values = list(header_row[1:6])
        self.team_a = values[0]
        self.team_b = values[1]
        self.winner = values[2]
        self.game_mode = values[3]
        self.map = values[4]

    def process_medal_row(self, medal_row):
        self.medals.append(tuple(medal_row[1:3]))
    
    def process_player_row(self, team_row):
        # convert stringss and floats to ints if possible
        team_row = pd.Series([try_convert_int(v) for v in team_row])

        if len(self.team_a_players) < TEAM_SIZE:
            self.team_a_players.append(list(team_row))
        else:
            self.team_b_players.append(list(team_row))


def parse_csv(csv_file) -> list[CSV_Game]:
    df = pd.read_csv(csv_file, header=None)

    # true if the previous row begins with no value
    prev_begins_null = False

    games = []
    current_game = None

    # iterate over the df, pop rows, and extract their data
    for index in df.index.tolist():
        row = df.loc[index]

        df = df.drop(index)

        if not prev_begins_null and pd.isna(row[0]):
            if current_game is not None:
                games.append(current_game)
            # New game
            prev_begins_null = True
            current_game = CSV_Game()
            current_game.process_header_row(row)

        elif prev_begins_null and pd.isna(row[0]):
            # Medal row
            current_game.process_medal_row(row)

        elif not pd.isna(row[0]):
            # Player row
            current_game.process_player_row(row)
            prev_begins_null = False

    if current_game is not None:
        games.append(current_game)

    return games

if __name__ == '__main__':
    games = parse_csv('app/testing/test.csv')
    for game in games:
        print('Teams:', game.team_a, game.team_b)
        print('Winner:', game.winner)
        print('Game Mode:', game.game_mode)
        print('Map:', game.map)
        print(game.medals)
        print(game.team_a_players)
        print(game.team_b_players)
        print('\n')
