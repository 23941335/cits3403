import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from app import app as main_app, db
from app.models import User, Role, Visibility 
import threading
import time

# This is a base class for all our Selenium browser tests.

class BaseSeleniumTests(unittest.TestCase):
    host = "http://127.0.0.1" 
    port = 5001
    base_url = f"{host}:{port}"
    
    _server_thread = None
    _app = None

    @classmethod
    def setUpClass(cls):
        """This special function runs once before any Selenium tests in a class start."""
        # Use the global app instance and reconfigure it for testing
        cls._app = main_app 
        cls._app.config['TESTING'] = True 
        cls._app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        cls._app.config['WTF_CSRF_ENABLED'] = False 
        cls._app.config['SERVER_NAME'] = f"127.0.0.1:{cls.port}" 
        cls._app.config['APPLICATION_ROOT'] = "/"
        cls._app.config['PREFERRED_URL_SCHEME'] = "http"

        # We need to ensure tables are created in the in-memory DB
        with cls._app.app_context():
            db.drop_all() # Drop existing tables if any.
            db.create_all() 
            # Add some default data if needed
            if not Visibility.query.first():
                db.session.add(Visibility(visibility="public"))
                db.session.add(Visibility(visibility="private"))
            if not Role.query.first(): # If no Roles exist
                db.session.add(Role(role_name="user")) # Add a basic 'user' role
            db.session.commit() # Save this initial data

        # Start the Flask server in a background thread
        cls._server_thread = threading.Thread(target=cls._app.run, kwargs={'host': '127.0.0.1', 'port': cls.port, 'use_reloader': False})
        cls._server_thread.daemon = True
        cls._server_thread.start()
        
        # Wait a tiny bit for the server to fully start up
        time.sleep(3) # Increased wait time for server startup

        # Set up the WebDriver
        try:
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless') 
            options.add_argument('--no-sandbox') 
            options.add_argument('--disable-dev-shm-usage') 
            
            # Automatically download and set up ChromeDriver
            cls.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        except Exception as e:
            print(f"Problem setting up ChromeDriver: {e}")
            raise
        
        cls.driver.implicitly_wait(5) 

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()


    def setUp(self):
        with self._app.app_context():
            # Delete data from tables that tests might change.
            from app.models import GameMedals, GamePlayers, Game, TournamentUsers, Tournament, User
            GameMedals.query.delete()
            GamePlayers.query.delete()
            Game.query.delete()
            TournamentUsers.query.delete()
            Tournament.query.delete()
            User.query.delete()
            db.session.commit() # Save these deletions to make tables empty

    def tearDown(self):
        with self._app.app_context():
            db.session.remove() # Clean up the database session


    def get_full_url(self, path):
        """A helper function to create a full URL, like http://127.0.0.1:5001/somepage """
        if path.startswith("/"): # If path already starts with /
            return self.base_url + path
        return self.base_url + "/" + path # Add / if missing

    def create_test_user(self, username="testuser", email="test@example.com", password="password"):
        """A helper function to quickly create a new user in the database for test setup."""
        with self._app.app_context():
            # Get the first role to assign to the new user
            user_role = Role.query.first() 
            if not user_role:
                user_role = Role(role_name="user")
                db.session.add(user_role)
                db.session.commit()

            user = User(username=username, email=email, global_role_id=user_role.id)
            user.set_password(password) # Hash the password
            db.session.add(user)
            db.session.commit() # Save the new user
            return user

if __name__ == '__main__':
    pass
