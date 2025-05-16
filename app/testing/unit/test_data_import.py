import os
import unittest
from pathlib import Path
from datetime import datetime

from app import app, db
from app.models import (
    Role,
    HeroRole,
    GameMode,
    Visibility,
    Map,
    Tournament,
    Game,
    GamePlayers,
    GameMedals,
    Player,
)
from data_import import import_csv
from seed import populate_heros
from app.consts import MAPS
# define map_list for testing
map_list = [item['name'] for gamemode in MAPS.values() for item in gamemode]
from app.forms import CreateTournamentForm
from werkzeug.datastructures import MultiDict


class TestDataImport(unittest.TestCase):
    """Tests for CSV data import using valid and invalid CSV files."""

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        db.drop_all()
        db.create_all()

        # seed lookup tables
        Role.populate_with_list('role_name', ['default', 'administrator', 'moderator', 'tournament_owner'])
        HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
        GameMode.populate_with_list('game_mode_name', ['domination', 'convoy', 'convergence'])
        Visibility.populate_with_list('visibility', ['public', 'private'])
        Map.populate_with_list('map_name', map_list, use_casefold=False)
        # seed heroes
        populate_heros()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # clear data tables
        Game.query.delete()
        Player.query.delete()
        GamePlayers.query.delete()
        GameMedals.query.delete()
        Tournament.query.delete()
        db.session.commit()

        # create a tournament record for import
        self.tournament = Tournament(
            title="Test Tournament",
            description="Desc",
            visibility_id=1,
            start_time=datetime.fromisoformat("2025-01-01T00:00")
        )
        db.session.add(self.tournament)
        db.session.commit()

    def test_valid_csv_import(self):
        valid_path = Path(__file__).parent / "valid.csv"
        result = import_csv(str(valid_path), self.tournament)
        self.assertTrue(result)
        # Expect 7 games from valid.csv
        self.assertEqual(Game.query.count(), 7)
        self.assertGreater(Player.query.count(), 0)
        self.assertGreater(GamePlayers.query.count(), 0)
        self.assertGreater(GameMedals.query.count(), 0)

    def test_invalid_csv_import(self):
        invalid_path = Path(__file__).parent / "invalid.csv"
        with self.assertRaises(Exception) as cm:
            import_csv(str(invalid_path), self.tournament)
        self.assertTrue(str(cm.exception))

        # simulate create tournament form validation similar to create_tournaments
        form = CreateTournamentForm(formdata=MultiDict())
        form.visibility.choices = [(-1, "- Select -")]
        self.assertFalse(form.validate())
        self.assertTrue(form.name.errors and form.visibility.errors)


if __name__ == "__main__":
    unittest.main()
