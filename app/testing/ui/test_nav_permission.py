from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.testing.ui.base_test import BaseSeleniumTests 
import time

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

    def test_authenticated_page_access_and_redirects(self):
        """
        Check if logged in users can see their pages, or sent to the login page.
        """
        driver = self.driver
        authenticated_pages = [
            "/account", 
            "/create-tournament",
        ]

        for page_path in authenticated_pages:
            driver.get(self.get_full_url(page_path))
        # Expect redirect to login for unauthenticated users
        # WebDriverWait(driver, 10).until(EC.url_contains("/account/login"))
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-button"))
        )
        self.assertIn("/account/login", driver.current_url)

    def test_404_error_page(self):
        """
        Test if 404 page shows up.
        """
        driver = self.driver
        non_existent_url = self.get_full_url("/sometimes")
        driver.get(non_existent_url)
        error_message_element = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, "error-message"))
        )
        self.assertTrue(error_message_element.is_displayed(), "Specific 404 error message not found.")
        return_link = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "return-home-link"))
        )
        self.assertTrue(return_link.is_displayed(), "'Return to Home Page' link not found.")

if __name__ == '__main__':
    unittest.main()
