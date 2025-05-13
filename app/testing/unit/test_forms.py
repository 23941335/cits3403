import unittest
from app import app as main_app, db
from app.models import User, Visibility
from app.forms import SignupForm, LoginForm, CreateTournamentForm
from werkzeug.datastructures import MultiDict


class TestForms(unittest.TestCase):
    """
    This class for signup, login, create valid tournament forms.
    """

    @classmethod
    def setUpClass(cls):
        cls.app = main_app
        cls.app.config['TESTING'] = True 
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        cls.app.config['WTF_CSRF_ENABLED'] = False 
        cls.app.config['SERVER_NAME'] = 'localhost.localdomain' 
        
        cls.app_context = cls.app.app_context()
        cls.app_context.push() 
        db.drop_all()
        db.create_all()

        vis_public = Visibility(visibility="public")
        vis_private = Visibility(visibility="private")
        db.session.add_all([vis_public, vis_private])
        db.session.commit() 


    @classmethod
    def tearDownClass(cls):
        db.session.remove() 
        db.drop_all() 
        cls.app_context.pop() 

    def setUp(self):
        try:
            db.session.rollback()
        except:
            pass

        User.query.delete() 
        db.session.commit()

        # Now create the 'existing_user'.
        self.existing_user = User(username="existinguser", email="existing@example.com", global_role_id=1)
        self.existing_user.set_password("password")
        db.session.add(self.existing_user)
        db.session.commit()
        
        # Use for rollback
        self.transaction = db.session.begin_nested()


    def tearDown(self):
        """This function runs after each individual test."""
        if self.transaction: # Check if transaction was successfully started
            try:
                self.transaction.rollback()
            except:
                # Try a full session rollback as a fallback
                db.session.rollback()
        db.session.remove() 

    # --- Key SignupForm Tests ---
    def test_signup_form_valid_data(self):
        """Test if the signup form works with all correct information."""
        formdata = MultiDict([
            ("username", "newuser"),
            ("email", "new@example.com"),
            ("password", "newpassword"),
            ("confirm_password", "newpassword")
        ])
        form = SignupForm(formdata=formdata)
        self.assertTrue(form.validate(), msg=f"Form errors: {form.errors}")

    def test_signup_form_duplicate_username(self):
        """Test signup form if username is already taken (critical validation)."""
        formdata = MultiDict([
            ("username", "existinguser"),
            ("email", "new@example.com"),
            ("password", "newpassword"),
            ("confirm_password", "newpassword")
        ])
        form = SignupForm(formdata=formdata)
        self.assertFalse(form.validate())
        self.assertIn("Please use a different username. This one is already taken.", form.username.errors)

    # --- Key LoginForm Test ---
    def test_login_form_valid_data_fields_present(self):
        """Test if the login form accepts data (checks if required fields are filled)."""
        formdata = MultiDict([
            ("username", "testuser"),
            ("password", "password")
        ])
        form = LoginForm(formdata=formdata)
        self.assertTrue(form.validate(), msg=f"Form errors: {form.errors}")

    def test_create_tournament_form_valid_data(self):
        """Test create tournament form with all correct information (core feature)."""
        visibilities = db.session.scalars(db.select(Visibility)).all()
        visibility_choices = [(-1, '- Select -')] + [(v.id, v.visibility.capitalize()) for v in visibilities]
        
        public_vis = Visibility.query.filter_by(visibility="public").first()
        self.assertIsNotNone(public_vis, "Public visibility option not found for test.")

        formdata = MultiDict([
            ("name", "My Awesome Tourney"),
            ("description", "A great tournament"),
            ("visibility", str(public_vis.id)),
            ("start_time", "2025-12-25T10:00") # DateTimeLocalField expects string in this format
        ])

        form = CreateTournamentForm(formdata=formdata)
        form.visibility.choices = visibility_choices # Set choices before validation
        
        self.assertTrue(form.validate(), msg=f"Form errors: {form.errors}")


if __name__ == '__main__':
    unittest.main()
