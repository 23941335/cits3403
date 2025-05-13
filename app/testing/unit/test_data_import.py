import unittest
from io import BytesIO
from app import app as main_app, db
from app.models import Tournament, Game, Team, Player, GameMode, Map, Hero, Medal, GamePlayers, GameMedals, Visibility, Role, HeroRole
import seed
from data_import import import_csv


SAMPLE_CSV_CONTENT_VALID = """
,Team Alpha,Team Bravo,Team Alpha,Domination,Birnin T'Challa,1
,MVP,Player1
,Fastest Cap,Player2
Player1,10,2,5,3,1500,500,200,50,Hulk
Player2,8,3,6,2,1200,300,100,40,Iron Man
Player3,12,1,4,5,1800,600,50,60,Loki
Player4,5,5,5,1,1000,200,800,30,Captain America
Player5,7,4,3,2,1100,400,0,45,Black Panther
Player6,6,3,7,1,900,100,0,35,Mantis
Player7,9,2,5,4,1400,450,150,55,Thor
Player8,4,6,2,1,800,250,50,30,Spider-Man
Player9,11,3,3,3,1600,550,0,65,Rocket Raccoon
Player10,3,7,1,0,700,150,700,25,Doctor Strange
Player11,8,4,6,2,1300,350,0,40,Star-Lord
Player12,5,5,5,1,1000,200,0,30,Invisible Woman
"""

MINIMAL_CSV_CONTENT_FOR_INVALID_ENTITIES = """
,Team Xyz,Team Pqr,Team Xyz,Payload,Route 66,1
PlayerNewA,1,0,0,1,100,0,0,10,Sombra
PlayerNewB,0,1,0,0,0,0,100,10,Brigitte
PlayerNewC,0,0,1,0,0,100,0,10,Sigma
PlayerNewD,1,0,0,1,100,0,0,10,Mei
PlayerNewE,0,1,0,0,0,0,100,10,Baptiste
PlayerNewF,0,0,1,0,0,100,0,10,D.Va
PlayerNewG,1,0,0,1,100,0,0,10,Ashe
PlayerNewH,0,1,0,0,0,0,100,10,Lucio
PlayerNewI,0,0,1,0,0,100,0,10,Wrecking Ball
PlayerNewJ,1,0,0,1,100,0,0,10,Pharah
PlayerNewK,0,1,0,0,0,0,100,10,Ana
PlayerNewL,0,0,1,0,0,100,0,10,Reinhardt
"""


class TestDataImport(unittest.TestCase):
    """
    Contains tests for the 'data_import.py' file
    """

    @classmethod
    def setUpClass(cls):
        cls.app = main_app
        cls.app.config['TESTING'] = True 
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        cls.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        cls.app.config['SERVER_NAME'] = 'localhost.localdomain' 
        
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all() # Ensure a clean state
        db.create_all()

        # Seeding
        print("Seeding test database...")
        Role.populate_with_list('role_name', ['default', 'administrator', 'moderator'])
        HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
        GameMode.populate_with_list('game_mode_name', ['domination', 'convoy', 'convergence'])
        Visibility.populate_with_list('visibility', ['public', 'private'])
        map_list = [map_item['name'] for gamemode in seed.MAPS.values() for map_item in gamemode]
        Map.populate_with_list('map_name', map_list, use_casefold=False) # Use original case from seed
        seed.populate_heros()
        print("Seeding complete.")

        vis = Visibility.query.filter_by(visibility="public").first()
        cls.default_visibility_id = vis.id if vis else None
    

    @classmethod
    def tearDownClass(cls):
        db.session.remove() 
        db.drop_all() 
        cls.app_context.pop() 

    def setUp(self):
        # Clear tables populated by import_csv before each test.
        GameMedals.query.delete()
        GamePlayers.query.delete()
        Game.query.delete()
        Medal.query.delete()
        Player.query.delete()
        Team.query.delete()
        db.session.commit()


        # Re-create the per-test tournament
        if self.default_visibility_id:
            self.tournament = Tournament(title="Test Tournament", description="Test Desc", visibility_id=self.default_visibility_id)
            db.session.add(self.tournament)
            db.session.commit()
        else:
            self.fail("Could not find 'public' visibility after seeding for test setup.")

    def tearDown(self):
        db.session.remove() 

    def test_import_csv_successful_import_and_data_check(self):
        """Test if 'import_csv' successfully imports data and verify database."""
        cleaned_csv_lines = [line for line in SAMPLE_CSV_CONTENT_VALID.splitlines() if line.strip()]
        csv_content_cleaned = "\n".join(cleaned_csv_lines)
        csv_bytes = csv_content_cleaned.encode('utf-8')
        csv_file_like = BytesIO(csv_bytes)
        
        initial_games_count = Game.query.count()
        initial_teams_count = Team.query.count()
        initial_players_count = Player.query.count()

        result = import_csv(csv_file_like, tournament=self.tournament, commit_changes=True)
        self.assertTrue(result) 

        self.assertGreater(Game.query.count(), initial_games_count) 
        self.assertEqual(Team.query.count(), initial_teams_count + 2) 
        self.assertEqual(Player.query.count(), initial_players_count + 12) 
        
        game = Game.query.filter_by(tournament_id=self.tournament.id).first() 
        self.assertIsNotNone(game) 
        self.assertEqual(game.team_a.team_name, "team alpha")

        # Fetch GameMode and Map explicitly using their IDs from the Game object
        game_mode_obj = db.session.get(GameMode, game.game_mode_id)
        self.assertIsNotNone(game_mode_obj)
        self.assertEqual(game_mode_obj.game_mode_name, "domination")

        map_obj = db.session.get(Map, game.map_id)
        self.assertIsNotNone(map_obj)
        self.assertEqual(map_obj.map_name, "Birnin T'Challa")

        player1_stats = GamePlayers.query.join(Player).filter(Player.gamertag == "Player1", GamePlayers.game_id == game.id).first()
        self.assertIsNotNone(player1_stats)
        self.assertEqual(player1_stats.kills, 10)

        hero_obj = db.session.get(Hero, player1_stats.hero_id)
        self.assertIsNotNone(hero_obj)
        self.assertEqual(hero_obj.hero_name, "Hulk") 

        mvp_medal_link = GameMedals.query.join(Medal).join(Player).filter(
            Medal.medal_name == "MVP", Player.gamertag == "Player1", GameMedals.game_id == game.id
        ).first()
        self.assertIsNotNone(mvp_medal_link)


    def test_import_csv_raises_error_for_invalid_entities(self):
        """See if 'import_csv' raises ValueError for Heroes, Maps, or GameModes not in the seeded data."""

        # Create a CSV-like string with invalid entities
        cleaned_csv_lines_invalid = [line for line in MINIMAL_CSV_CONTENT_FOR_INVALID_ENTITIES.splitlines() if line.strip()]
        csv_content_invalid_cleaned = "\n".join(cleaned_csv_lines_invalid)
        csv_bytes_invalid = csv_content_invalid_cleaned.encode('utf-8')
        csv_file_like_invalid = BytesIO(csv_bytes_invalid)

        # Assert that calling import_csv with this data raises a ValueError
        with self.assertRaises(ValueError) as cm:
            import_csv(csv_file_like_invalid, tournament=self.tournament, commit_changes=True)

        # Check the error message contains expected info.
        error_message = str(cm.exception).lower()
        self.assertTrue("invalid game mode" in error_message or "invalid map" in error_message or "invalid hero" in error_message,
                        f"Expected ValueError for invalid entity, but got: {cm.exception}")
        # Example check for specific invalid item:
        self.assertTrue("payload" in error_message or "route 66" in error_message or "sombra" in error_message,
                        f"Error message did not contain expected invalid item name: {cm.exception}")

        # Also verify that no partial data was committed due to the error
        game_count_after_error = Game.query.filter_by(tournament_id=self.tournament.id).count()
        self.assertEqual(game_count_after_error, 0, "Game data was committed despite encountering an invalid entity.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
