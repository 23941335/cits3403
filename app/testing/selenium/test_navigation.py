from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.testing.selenium.base_test import BaseSeleniumTests 

class TestNavigation(BaseSeleniumTests):
    """
    This class tests the permission when users navigate around the public / private pages.
    """

    def test_public_page_accessibility_anonymous(self):
        """
        If anonymous users can see public pages.
        """
        driver = self.driver
        public_pages = ["/", "/home", "/account/login", "/account/signup", "/history"]
        
        for page_path in public_pages:
            driver.get(self.get_full_url(page_path)) 
            self.assertTrue(driver.current_url.endswith(page_path) or \
                            (page_path == "/" and driver.current_url.endswith("/home")), 
                            f"Could not load public page: {page_path}")

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.assertTrue(driver.find_element(By.TAG_NAME, "body").is_displayed(), 
                            f"The body of the page {page_path} was not displayed.")

    def test_authenticated_page_access_and_redirects(self):
        """
        Check if logged in users can see their pages, or sent to the login page.
        """
        driver = self.driver
        authenticated_pages = [
            "/account", 
            "/create-tournament",
            "/tournament",
            "/tournament/game",
            "/tournament/team",
            "/tournament/player"
        ]

        self.create_test_user(username="random", email="nave@lala.com", password="188741123")
        driver.get(self.get_full_url("/account/login"))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys("random")
        driver.find_element(By.ID, "password").send_keys("188741123")
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID , "login-button")))
        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/home")) # After login, should redirect to home

        for page_path in authenticated_pages:
            driver.get(self.get_full_url(page_path))
            # Should stay on the requested page
            WebDriverWait(driver, 10).until(EC.url_to_be(self.get_full_url(page_path)))
            self.assertEqual(driver.current_url, self.get_full_url(page_path),
                             f"Logged-in user could not access {page_path}")
            self.assertTrue(driver.find_element(By.TAG_NAME, "body").is_displayed(),
                             f"The body of page {page_path} was not displayed for logged-in user.")

    def test_404_error_page(self):
        """
        Test if 404 page shows up.
        """
        driver = self.driver
        non_existent_url = self.get_full_url("/sometimes")
        driver.get(non_existent_url)
        error_message_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "error-message"))
        )
        self.assertTrue(error_message_element.is_displayed(), "Specific 404 error message not found.")
        return_link = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "return-home-link"))
        )
        self.assertTrue(return_link.is_displayed(), "'Return to Home Page' link not found.")

if __name__ == '__main__':
    unittest.main()
