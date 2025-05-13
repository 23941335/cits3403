import unittest
from app.models import User 

class TestUserModel(unittest.TestCase):
    """
    This class contains tests for the User model.
    """

    def test_password_hashing_and_checking(self):
        """
        Checks if passwords are being handled securely.
        """

        # Create a new user for testing
        u = User(username="testuser", email="test@example.com")
        u.set_password("correctpassword")

        # Check if the password was stored and is not plain text
        self.assertIsNotNone(u.password_hash) # Should not be empty
        self.assertNotEqual(u.password_hash, "correctpassword")  # Should be hashed
        
        # Check if the correct password works
        self.assertTrue(u.check_password("correctpassword"))
        # Check if an incorrect password fails
        self.assertFalse(u.check_password("incorrectpassword"))

if __name__ == '__main__':
    unittest.main()
