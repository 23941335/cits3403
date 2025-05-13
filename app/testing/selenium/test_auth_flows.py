import random
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.testing.selenium.base_test import BaseSeleniumTests
from app.models import User  # Database assertions


def generate_random_username(length=8):
    return f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"


def generate_random_email():
    return f"test_{''.join(random.choices(string.ascii_lowercase, k=6))}@lala.com"


class TestAuthFlows(BaseSeleniumTests):
    """
    How users sign up, log in, and log out.
    It inherits from BaseSeleniumTests to get the browser and server up.
    """

    def test_successful_user_signup(self):
        test_username = generate_random_username()
        test_email = generate_random_email()
        test_password = "TestMeowMeow!"

        driver = self.driver 
        driver.get(self.get_full_url("/account/signup")) 
        driver.find_element(By.ID, "username").send_keys(test_username)
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirm_password").send_keys(test_password)
        driver.find_element(By.ID, "submit").click() 

        # After that, the page should show a flash message.
        WebDriverWait(driver, 10).until(EC.url_contains("/account/login"))
        self.assertIn("/account/login", driver.current_url)

        flash_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "success-message"))
        )
        self.assertIn("Your account has been created!", flash_message.text)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        driver.find_element(By.ID, "username").send_keys(test_username)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "login-button").click()

        # After successful login, should redirect to home
        WebDriverWait(driver, 10).until(EC.url_contains("/home"))
        self.assertIn("/home", driver.current_url)  # Final landing page

        # Check if the user was actually added to the database.
        with self._app.app_context():
            user = User.query.filter_by(username=test_username).first()
            self.assertIsNotNone(user)  # User should exist
            self.assertEqual(user.email, test_email)  # Email should match

    def test_successful_user_login_and_logout(self):
        """
        See if a user can log in with correct details and then log out.
        """
        test_username = generate_random_username()
        test_password = "TestMeowMeow!"

        self.create_test_user(
            username=test_username,
            email=generate_random_email(),
            password=test_password,
        )

        driver = self.driver
        driver.get(self.get_full_url("/account/login"))

        driver.find_element(By.ID, "username").send_keys(test_username)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "login-button").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/home"))
        self.assertIn("/home", driver.current_url)

        # Check for "Log Out" link.
        logout_link = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "logout-link"))
        )
        self.assertTrue(logout_link.is_displayed())  # It should be visible

        logout_link.click()
        # After that, user should be sent to the "/".
        WebDriverWait(driver, 10).until(
            EC.url_to_be(self.get_full_url("/"))
        )  

        login_link = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-link"))
        )
        self.assertTrue(login_link.is_displayed())

    def test_user_login_with_invalid_credentials(self):
        """
        Test wrong username/password.
        """
        invalid_username = generate_random_username()
        invalid_password = "WrongPass123!"

        driver = self.driver
        driver.get(self.get_full_url("/account/login"))

        driver.find_element(By.ID, "username").send_keys(invalid_username)
        driver.find_element(By.ID, "password").send_keys(invalid_password)
        driver.find_element(By.ID, "login-button").click()

        # Should stay and have error flash message.
        WebDriverWait(driver, 10).until(EC.url_contains("/account/login"))
        flash_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "danger-message"))
        )
        self.assertIn(
            "Invalid username or password", flash_message.text
        )


# This allows running tests directly if you execute this file.
if __name__ == "__main__":
    unittest.main()
