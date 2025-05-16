import unittest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from app.testing.ui.base_test import BaseSeleniumTests
from app import db
from app.models import Tournament, Visibility, Role, HeroRole, GameMode, Map, Game, Team, Player, GamePlayers, GameMedals, Medal
from data_import import split_line, process_lines, MATCH_ROUND
from seed import MAPS, populate_heros

class TestUIDataImport(BaseSeleniumTests):
    """
    Tests the CSV data import functionality via the Create Tournament UI and Database.
    """

    @classmethod
    def setUpClass(cls):
        super(TestUIDataImport, cls).setUpClass()
        with cls._app.app_context():
            HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
            GameMode.populate_with_list('game_mode_name', ['domination', 'convoy', 'convergence'])
            # Extract all map names from the nested MAPS structure for populating the database
            map_list = []
            for game_mode_maps in MAPS.values():
                for map_dict in game_mode_maps:
                    map_list.append(map_dict['name'])
            Map.populate_with_list('map_name', map_list, use_casefold=False)
            populate_heros()
            db.session.commit()
            Role.populate_with_list('role_name', ['tournament_owner'])
            db.session.commit()

        with cls._app.app_context():
            vis = Visibility.query.filter_by(visibility="public").first()
            cls.public_visibility_id = vis.id if vis else None

    def setUp(self):
        super().setUp()
        with self._app.app_context():
            GameMedals.query.delete()
            GamePlayers.query.delete()
            Game.query.delete()
            Medal.query.delete()
            Player.query.delete()
            Team.query.delete()
            db.session.commit()
        self.create_test_user(username="csv_tester", email="csv@test.com", password="password")
        self.login_user("csv_tester", "password")

    def tearDown(self):
        try:
            l = self.driver.find_element(By.ID, "logout-link")
            if l.is_displayed():
                l.click()
                WebDriverWait(self.driver, 5).until(EC.url_contains("/account/login"))
        except Exception:
            pass
        super().tearDown()

    def login_user(self, username, password):
        driver = self.driver
        driver.get(self.get_full_url("/account/login"))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/home"))

    def test01_create_tournament_with_valid_csv(self):
        driver = self.driver
        driver.get(self.get_full_url("/create-tournament"))

        tournament_name = "Valid CSV Import Test"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))
        driver.find_element(By.ID, "name").send_keys(tournament_name)
        driver.find_element(By.ID, "description").send_keys("Testing valid CSV upload.")
        dt = "2025-05-20T16:30"
        start_el = driver.find_element(By.ID, "start_time")
        driver.execute_script("arguments[0].value = arguments[1];", start_el, dt)
        sel = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "view"))))
        sel.select_by_visible_text("Public")
        valid_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'valid.csv'))
        self.assertTrue(os.path.exists(valid_csv_path), f"CSV file not found at {valid_csv_path}")

        driver.find_element(By.ID, "results_file").send_keys(valid_csv_path)
        driver.find_element(By.ID, "teams").send_keys("Team Test")
        submit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Create Tournament']")))
        submit.click()
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "success-message")))
        
        # Database assertions driven by parser
        with self._app.app_context():
            tour = Tournament.query.filter_by(title=tournament_name).first()
            self.assertIsNotNone(tour, "Tournament not created.")
            # parse CSV
            with open(valid_csv_path, 'r') as rf:
                rows = [split_line(l) for l in rf]
            games_data = process_lines(rows)
            for header, medal_rows, player_rows in games_data:
                rnd = int(header[MATCH_ROUND])
                game_db = Game.query.filter_by(tournament_id=tour.id, round=rnd).first()
                self.assertIsNotNone(game_db, f"Game round {rnd} missing.")
                # players count
                self.assertEqual(GamePlayers.query.filter_by(game_id=game_db.id).count(), len(player_rows))
                # medals count
                self.assertEqual(GameMedals.query.filter_by(game_id=game_db.id).count(), len(medal_rows))
                # detailed stats verification omitted; using parser-driven counts only

    def test02_create_tournament_with_invalid_csv(self):
        driver = self.driver
        driver.get(self.get_full_url("/create-tournament"))
        name = "Invalid CSV Import Test"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))
        driver.find_element(By.ID, "name").send_keys(name)
        driver.find_element(By.ID, "description").send_keys("Testing invalid CSV upload.")
        dt = "2025-02-20T16:30"
        el = driver.find_element(By.ID, "start_time")
        driver.execute_script("arguments[0].value = arguments[1];", el, dt)
        Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "view")))).select_by_visible_text("Public")
        
        # Construct the absolute path to the 'invalid.csv' file located in the same directory as this test script
        current_directory = os.path.dirname(__file__)
        invalid_csv_filename = 'invalid.csv'
        invalid_path = os.path.abspath(os.path.join(current_directory, invalid_csv_filename))
        self.assertTrue(os.path.exists(invalid_path), f"CSV file not found at {invalid_path}")
        driver.find_element(By.ID, "results_file").send_keys(invalid_path)
        driver.find_element(By.ID, "teams").send_keys("Team Test")
        btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Create Tournament']")))
        btn.click()
        msg = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "danger-message")))
        self.assertIn("Tournament creation failed!", msg.text)
        with self._app.app_context():
            self.assertEqual(Game.query.count(), 0)
            self.assertEqual(Player.query.count(), 0)
            self.assertEqual(Medal.query.count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
