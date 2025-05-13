import unittest
import os
import time # Import time for potential waits
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from app.testing.selenium.base_test import BaseSeleniumTests
from app import db
from app.models import Tournament, Visibility, HeroRole, GameMode, Map, Hero, Game, Team, Player, GamePlayers, GameMedals, Medal
import seed


class TestUIDataImport(BaseSeleniumTests):
    """
    Tests the CSV data import functionality via the Create Tournament UI and a TEMP Database.
    """

    @classmethod
    def setUpClass(cls):
        super(TestUIDataImport, cls).setUpClass()

        with cls._app.app_context():
            # Seeding 
            HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
            GameMode.populate_with_list('game_mode_name', ['domination', 'convoy', 'convergence'])
            map_list = [map_item['name'] for gamemode in seed.MAPS.values() for map_item in gamemode]
            Map.populate_with_list('map_name', map_list, use_casefold=False) # Check if case sensitivity matches CSV
            seed.populate_heros() # Check hero names/casing vs CSV
            db.session.commit()
            print("Seeding complete.")

        with cls._app.app_context():
            vis = Visibility.query.filter_by(visibility="public").first()
            cls.public_visibility_id = vis.id if vis else None
            if not cls.public_visibility_id:
                 print("! Could not find 'public' visibility ID.")


    @classmethod
    def tearDownClass(cls):
        super(TestUIDataImport, cls).tearDownClass()
        # time.sleep(303239222)


    def setUp(self):
        """Runs before each test method."""
        super().setUp()
        with self._app.app_context():
            GameMedals.query.delete()
            GamePlayers.query.delete()
            Game.query.delete()
            Medal.query.delete()
            Player.query.delete()
            Team.query.delete()
            db.session.commit()
        self.test_user = self.create_test_user(username="csv_tester", email="csv@test.com", password="password")
        self.login_user(username="csv_tester", password="password")

    def tearDown(self):
        driver = self.driver
        # Attempt to log out
        try:
            logout_link = WebDriverWait(driver, 5).until( 
                EC.visibility_of_element_located((By.ID, "logout-link"))
            )
            if logout_link.is_displayed():
                logout_link.click()
                WebDriverWait(driver, 5).until(EC.url_contains(self.get_full_url("/account/login")))
        except Exception as e:
            print(f"DEBUG: Could not perform logout in tearDown (may already be logged out or on an error page): {e}")
        super().tearDown()


    def login_user(self, username, password):
        """log in a user."""
        driver = self.driver
        driver.get(self.get_full_url("/account/login"))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "login-button")))
        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/home"))

    def test01_create_tournament_with_valid_csv(self):
        """Creating a tournament with a valid CSV"""
        driver = self.driver
        driver.get(self.get_full_url("/create-tournament"))

        tournament_name = "Valid CSV Import Test"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))

        # Fill form fields
        driver.find_element(By.ID, "name").send_keys(tournament_name)
        driver.find_element(By.ID, "description").send_keys("Testing valid CSV upload.")
        # Ensure the date format matches the input type="datetime-local"
        date_string = "2017-06-30T16:30"
        # Js to set the value
        driver.execute_script(f"arguments[0].value = '{date_string}';", date_string)

        # Select visibility
        visibility_select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "view"))
        )
        visibility_select = Select(visibility_select_element)
        self.assertIsNotNone(self.public_visibility_id, "Public visibility ID not found after seeding.")
        visibility_select.select_by_visible_text("Public")
        valid_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'valid_data.csv'))

        self.assertTrue(os.path.exists(valid_csv_path), f"CSV file not found at calculated path: {valid_csv_path}")

        try:
            # Upload the valid CSV
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "results_file"))
            )
            file_input.send_keys(valid_csv_path)
            driver.find_element(By.ID, "teams").send_keys("Team Test") 

            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Create Tournament']"))
            )

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            submit_button.click()

            flash_message = WebDriverWait(driver, 20).until( # Increased wait time
                EC.visibility_of_element_located((By.ID, "success-message"))
            )
            self.assertIn("Tournament created!", flash_message.text)

            # Database Assertions
            print("DEBUG: Asserting database entries...")
            with self._app.app_context():
                tournament = Tournament.query.filter_by(title=tournament_name).first()
                self.assertIsNotNone(tournament, "Tournament not found in DB after valid CSV import.")
                # Check game count
                expected_game_count = 2
                self.assertEqual(Game.query.filter_by(tournament_id=tournament.id).count(), expected_game_count, f"Expected {expected_game_count} game(s) created.")

                # Check specific player/hero/medal
                player = Player.query.filter_by(gamertag="PlayerName1").first()
                self.assertIsNotNone(player, "Player 'PlayerName1' not found.")

                game = Game.query.filter_by(tournament_id=tournament.id).first()
                self.assertIsNotNone(game, "Game not found for the tournament.")

                hero = Hero.query.filter_by(hero_name="Groot").first()
                self.assertIsNotNone(hero, "Hero 'Groot' not found.")

                gp_entry = GamePlayers.query.filter_by(game_id=game.id, player_id=player.id, hero_id=hero.id).first()
                self.assertIsNotNone(gp_entry, "GamePlayers entry for PlayerName1/Groot not found.")
                self.assertEqual(gp_entry.kills, 8, "Incorrect kills for PlayerName1/Groot.") # Verify kill count

                # Check medal
                medal = Medal.query.filter_by(medal_name="SVP").first()
                self.assertIsNotNone(medal, "Medal 'SVP' not found (should have been created by import).")

                gm_entry = GameMedals.query.filter_by(game_id=game.id, medal_id=medal.id, player_id=player.id).first()
                self.assertIsNotNone(gm_entry, "GameMedals entry for PlayerName1/SVP not found.")
            print("DEBUG: Database assertions passed.")

        except Exception as e:
             print(f"ERROR: Test failed during execution. Error: {e}")
             # Capture screenshot on failure
             timestamp = time.strftime("%Y%m%d-%H%M%S")
             screenshot_file = f"failure_screenshot_{timestamp}.png"
             try:
                 driver.save_screenshot(screenshot_file)
                 print(f"Screenshot saved to {screenshot_file}")
             except Exception as ss_err:
                 print(f"Failed to save screenshot: {ss_err}")
        
    def test02_create_tournament_with_invalid_csv(self):
        """Tests creating a tournament with an invalid CSV upload via the UI."""
        print("\nDEBUG: Starting test_create_tournament_with_invalid_csv")
        driver = self.driver
        driver.get(self.get_full_url("/create-tournament"))

        tournament_name = "Invalid CSV Import Test"


        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))

        driver.find_element(By.ID, "name").send_keys(tournament_name)
        driver.find_element(By.ID, "description").send_keys("Testing invalid CSV upload.")

        date_string = "2017-06-30T16:30"
        print(f"DEBUG: Setting start_time value using JavaScript to: {date_string}")
        driver.execute_script(f"arguments[0].value = '{date_string}';", date_string)

        visibility_select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "view"))
        )
        visibility_select = Select(visibility_select_element)
        self.assertIsNotNone(self.public_visibility_id, "Public visibility ID not found after seeding.")
        visibility_select.select_by_visible_text("Public") 

        invalid_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'invalid_data.csv'))
        print(f"DEBUG: Attempting to use invalid CSV path: {invalid_csv_path}")
        self.assertTrue(os.path.exists(invalid_csv_path), f"Invalid CSV file not found at calculated path: {invalid_csv_path}")

        try:

            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "results_file"))
            )
            file_input.send_keys(invalid_csv_path)

            
            driver.find_element(By.ID, "teams").send_keys("Team Test")

            # Submit Form
            print("DEBUG: Locating and clicking submit button...")
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Create Tournament']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            submit_button.click()
            print("DEBUG: Submit button clicked.")

            # --- Assert Error ---
            # We expect an error message since the CSV is invalid
            print("DEBUG: Waiting for error flash message...")
            flash_message = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, "danger-message"))
            )
            print(f"DEBUG: Found flash message: {flash_message.text}")
            self.assertIn("Error", flash_message.text, "Expected error message not found")

            # Database Assertions
            print("DEBUG: Asserting no database entries were created...")
            with self._app.app_context():
                tournament = Tournament.query.filter_by(title=tournament_name).first()
                self.assertIsNone(tournament, "Tournament should not be created with invalid CSV")
                
                # Verify no games were created
                self.assertEqual(Game.query.count(), 0, "No games should be created with invalid CSV")
                
                # Verify no players were created
                self.assertEqual(Player.query.count(), 0, "No players should be created with invalid CSV")
                
                # Verify no medals were created
                self.assertEqual(Medal.query.count(), 0, "No medals should be created with invalid CSV")
            print("DEBUG: Database assertions passed.")

        except Exception as e:
            print(f"ERROR: Test failed during execution. Error: {e}")
            # Capture screenshot on failure
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_file = f"failure_screenshot_{timestamp}.png"
            try:
                driver.save_screenshot(screenshot_file)
                print(f"Screenshot saved to {screenshot_file}")
            except Exception as ss_err:
                print(f"Failed to save screenshot: {ss_err}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
