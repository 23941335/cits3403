from app import models as m
from app import app, db
from sqlalchemy.exc import IntegrityError
from io import TextIOWrapper

TEST_FILE = "app/testing/test.csv"

# CONSTANTS
TEAM_SIZE = 6
PLACEHOLDER_ID = 1

# Indexes
MATCH_TEAM_A = 1
MATCH_TEAM_B = 2
MATCH_WINNER = 3
MATCH_GAME_MODE = 4
MATCH_MAP = 5

MEDAL_NAME = 1
MEDAL_PLAYER = 2

PLAYER_NAME = 0
PLAYER_KILLS = 1
PLAYER_DEATHS = 2
PLAYER_ASSISTS = 3
PLAYER_FINAL_HITS = 4
PLAYER_DAMAGE = 5
PLAYER_DAMAGE_BLOCKED = 6
PLAYER_HEALING = 7
PLAYER_ACCURACY = 8
PLAYER_HERO = 9


def split_line(line: str):
    return line.rstrip('\n').split(',')

def process_lines(line_list):
    games = []
    prev_started_blank = False
    header_row = None
    medal_rows = []
    player_rows = []

    for row in line_list:
        # If this line starts with a '' value and the previous line did not
        # then a new game is being read.
        if not row[0]:
            if not prev_started_blank:
                if header_row:
                    games.append((header_row, medal_rows, player_rows))
                header_row = row
                medal_rows = []
                player_rows = []
                prev_started_blank = True
            else:
                medal_rows.append(row)
        else:
            player_rows.append(row)
            prev_started_blank = False

    if header_row:
        games.append((header_row, medal_rows, player_rows))

    return games


class CSV_Game:
    def __init__(self, game_header_row, game_medal_rows, game_player_rows):
        self.game = None
        self.header_row = game_header_row
        self.medal_rows = game_medal_rows
        self.player_rows = game_player_rows 

    def create_game(self):
        header_row = self.header_row

        team_a_name = header_row[MATCH_TEAM_A].lower()
        team_b_name = header_row[MATCH_TEAM_B].lower()
        winning_team_name = header_row[MATCH_WINNER].lower()

        game_mode_name = header_row[MATCH_GAME_MODE].lower()
        map_name = header_row[MATCH_MAP].lower()

        # Find or create teams
        team_a = db.session.query(m.Team).filter_by(team_name=team_a_name).first()
        team_b = db.session.query(m.Team).filter_by(team_name=team_b_name).first()
        if not team_a:
            team_a = m.Team(team_name=team_a_name)
            db.session.add(team_a)
        if not team_b:
            team_b = m.Team(team_name=team_b_name)
            db.session.add(team_b)

        winning_team_id = None
        if winning_team_name in (team_a_name, team_b_name):
            winning_team = db.session.query(m.Team).filter_by(team_name=winning_team_name).first()
            winning_team_id = winning_team.id

        # Find or create game mode and map
        # NOTE: this shouldn't be needed if we just include all modes
        # and same goes for maps. This also prevents good error checking.

        game_mode = db.session.query(m.GameMode).filter_by(game_mode_name=game_mode_name).first()
        if not game_mode:
            game_mode = m.GameMode(game_mode_name=game_mode_name)
            db.session.add(game_mode)
        
        game_map = db.session.query(m.Map).filter_by(map_name=map_name).first()
        if not game_map:
            game_map = m.Map(map_name=map_name)
            db.session.add(game_map)

        db.session.flush()
        
        new_game = m.Game(
            tournament_id=PLACEHOLDER_ID, 
            round=PLACEHOLDER_ID,
            team_a_id=team_a.id,
            team_b_id=team_b.id,
            winning_team=winning_team_id,
            is_draw=(winning_team_id is None),
            game_mode_id=game_mode.id,
            map_id=game_map.id
        )

        db.session.add(new_game)
        db.session.flush()
        
        self.game = new_game

    def insert_players(self):
        player_row_list = self.player_rows

        for i, player_row in enumerate(player_row_list):
            if i > 11:
                raise ValueError("Too many players in CSV file")
            
            player_name = player_row[PLAYER_NAME]

            # Find or create players
            player = db.session.query(m.Player).filter_by(gamertag=player_name).first()
            if not player:
                player = m.Player(gamertag=player_name)
                db.session.add(player)
            
            # First 6 players are Team A, the next 6 are Team B. 
            team = self.game.team_a if i < 6 else self.game.team_b

            # TODO: If these are added in the DB, dont need to to do this.
            hero_name = player_row[PLAYER_HERO].lower()
            hero = db.session.query(m.Hero).filter_by(hero_name=hero_name).first()
            if not hero:
                hero = m.Hero(hero_name=hero_name, hero_role_id=PLACEHOLDER_ID)
                db.session.add(hero)

            kills = player_row[PLAYER_KILLS]
            deaths = player_row[PLAYER_DEATHS]
            assists = player_row[PLAYER_ASSISTS]
            final_hits = player_row[PLAYER_FINAL_HITS]
            damage = player_row[PLAYER_DAMAGE]
            damage_blocked = player_row[PLAYER_DAMAGE_BLOCKED]
            healing = player_row[PLAYER_HEALING]
            accuracy_pct = player_row[PLAYER_ACCURACY]
            
            db.session.flush()

            game_players = m.GamePlayers(
                game_id=self.game.id,
                player_id=player.id,
                team_id=team.id,
                hero_id=hero.id,
                kills=kills,
                deaths=deaths,
                assists=assists,
                final_hits=final_hits,
                damage=damage,
                damage_blocked=damage_blocked,
                healing=healing,
                accuracy_pct=accuracy_pct,
            )

            db.session.add(game_players)
            db.session.flush()


    def insert_medals(self):
        medal_row_list = self.medal_rows

        for medal_row in medal_row_list:
            player_name = medal_row[MEDAL_PLAYER]
            medal_name = medal_row[MEDAL_NAME]

            # Find or create players
            player = db.session.query(m.Player).filter_by(gamertag=player_name).first()
            if not player:
                player = m.Player(gamertag=player_name)
                db.session.add(player)
            
            # Find or create medals
            # TODO: these should just be stored in the DB, but need to know them all.
            medal = db.session.query(m.Medal).filter_by(medal_name=medal_name).first()
            if not medal:
                medal = m.Medal(medal_name=medal_name)
                db.session.add(medal)
            
            db.session.flush()

            game_medals = m.GameMedals(
                game_id=self.game.id, 
                medal_id=medal.id, 
                player_id=player.id
            )

            db.session.add(game_medals)
            db.session.flush()

    def create_changes(self):
        self.create_game()
        self.insert_players()
        self.insert_medals()

    def commit_changes(self):
        db.session.commit()

def import_csv(csv):
    # if a file path (for local testing)
    if isinstance(csv, str):
        with open(csv, 'r') as rf:
            lines = [split_line(l) for l in rf]
    
    # uploaded from website
    else:
        # convert it from bytes into readable text
        csv = TextIOWrapper(csv, encoding='utf-8')
        lines = [split_line(l) for l in csv]

    game_list = process_lines(lines)
    
    for game in game_list:
        csvg = CSV_Game(game[0], game[1], game[2])
        csvg.create_changes()
        # error checking here
        csvg.commit_changes()
    
    return True
    
if __name__ == '__main__':
    with app.app_context():
        import_csv(TEST_FILE)