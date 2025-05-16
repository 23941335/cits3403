import os
import unittest
from app import app as main_app, db
from app.models import User, Visibility
from app.forms import SignupForm, LoginForm, CreateTournamentForm
from werkzeug.datastructures import MultiDict


class TestForms(unittest.TestCase):
    """Core tests for form validation: signup, login, create tournament."""

    @classmethod
    def setUpClass(cls):
        cls.app = main_app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        # seed visibility options
        db.session.add_all([
            Visibility(visibility="public"),
            Visibility(visibility="private")
        ])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # clear users
        User.query.delete()
        db.session.commit()
        # add existing user
        user = User(username="existing", email="exists@example.com", global_role_id=1)
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_signup_form_valid(self):
        form = SignupForm(formdata=MultiDict([
            ("username", "newuser"),
            ("email", "new@example.com"),
            ("password", "securepass"),
            ("confirm_password", "securepass")
        ]))
        self.assertTrue(form.validate(), msg=form.errors)

    def test_signup_duplicate_username(self):
        form = SignupForm(formdata=MultiDict([
            ("username", "existing"),
            ("email", "new2@example.com"),
            ("password", "pass1234"),
            ("confirm_password", "pass1234")
        ]))
        self.assertFalse(form.validate())
        self.assertIn("Please use a different username.", form.username.errors[0])

    def test_signup_duplicate_email(self):
        form = SignupForm(formdata=MultiDict([
            ("username", "unique"),
            ("email", "exists@example.com"),
            ("password", "pass1234"),
            ("confirm_password", "pass1234")
        ]))
        self.assertFalse(form.validate())
        self.assertIn("Please use a different email address.", form.email.errors[0])

    def test_signup_password_mismatch(self):
        form = SignupForm(formdata=MultiDict([
            ("username", "userx"),
            ("email", "ux@example.com"),
            ("password", "abc12345"),
            ("confirm_password", "different")
        ]))
        self.assertFalse(form.validate())
        self.assertIn("Passwords do not match.", form.password.errors[0])

    def test_login_form_valid(self):
        form = LoginForm(formdata=MultiDict([
            ("username", "existing"),
            ("password", "password")
        ]))
        self.assertTrue(form.validate(), msg=form.errors)

    def test_create_tournament_valid(self):
        vis = Visibility.query.filter_by(visibility="public").first()
        form = CreateTournamentForm(formdata=MultiDict([
            ("name", "Tournament"),
            ("description", "Desc"),
            ("visibility", str(vis.id)),
            ("start_time", "2025-12-25T10:00")
        ]))
        # set choices
        opts = [(-1, "- Select -")] + [(v.id, v.visibility) for v in Visibility.query.all()]
        form.visibility.choices = opts
        self.assertTrue(form.validate(), msg=form.errors)

    def test_create_tournament_missing_fields(self):
        form = CreateTournamentForm(formdata=MultiDict())
        form.visibility.choices = [(-1, "- Select -")]
        self.assertFalse(form.validate())
        self.assertTrue(form.name.errors and form.visibility.errors)


    def test_password_hashing(self):
        """Test that setting a password stores a hashed value and verifies correctly."""
        user = User(username="testhash", email="hash@example.com", global_role_id=1)
        user.set_password("1887415157")
        # Password hash should not equal the raw password
        self.assertNotEqual(user.password_hash, "1887415157")
        # check_password should validate the hash correctly
        self.assertTrue(user.check_password("1887415157"))

if __name__ == '__main__':
    unittest.main()
