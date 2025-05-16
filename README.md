# CITS3403 Group Project

## Description

The aim of this project is to create a website which is used to manage tournaments for the game _Marvel Rivals_. Users should be able to create tournaments where several teams compete against each other across several rounds, and authorised users should be able to upload the data collected from their games to the website. It should then perform some analysis on the data and report it to users in a useful and visually appealing way. Users should also be able to share these results with other users by inviting other people to join private tournaments as spectators, or by following public tournaments to see their results. 

## Contributors
| Student Number | Name            | GitHub Username |
|----------------|-----------------|-----------------|
| 23941335       | George Brice    | 23941335        |
| 22666335       | Koda(Zhengxun) Lan        | Kod4-lan        |
| 23769985       | Max Moltoni     | SuperMax732     |
| 24240636       | Dongkai Liu     | itchat          |

## Planning and Meeting Notes
https://github.com/23941335/cits3403/blob/main/planning.md

## Setup

### Quick Start Instructions

#### Virtual environment:
```
python -m venv .venv
```
Depending on OS:

`source .venv/bin/activate` (Linux/MacOS)

`.venv\Scripts\activate` (Windows)

`source .venv/Scripts/activate` (WSL)

```
pip install -r requirements.txt
export SECRET_KEY='somevaluehere'
```
#### Build the database:
```
flask db upgrade
python seed.py
```
#### Start the server:
```
flask run
```

### Backend

#### Python Package Dependencies
- [email_validator](https://github.com/JoshData/python-email-validator)
- [Flask](https://github.com/pallets/flask)
- [Flask-Login](https://github.com/maxcountryman/flask-login)
- [Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)
- [Flask-SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy/)
- [Flask-WTF](https://github.com/pallets-eco/flask-wtf/) <!-- cf. lecture 9, slide 31 -->

Any other requirements listed in the requirements.txt are dependencies of these packages.

#### Virtual environment:
Create:
```
python -m venv .venv
```
Activate:

`source .venv/bin/activate` (Linux/MacOS)

`.venv\Scripts\activate` (Windows)

`source .venv/Scripts/activate` (WSL)

Install requirements:

```
pip install -r requirements.txt
```


If you want to delete the .venv:

`rd /s /q .venv` (Windows)

`rm -rf .venv` (Linux/MacOS)

#### Database

If you do not yet have the app.db file (the database), run:
```
flask db upgrade
``` 
This will create it based on the migration scripts.

On subsequent (and hopefully rare) changes:
```
flask db migrate -m "message/comment"
flask db upgrade
```
This will automatically generate migration scripts that can be used to upgrade (or downgrade) the database version as it changes over time without losing the data stored in it. 

## Testing

Note: Selenium testing requires that you have Google Chrome installed.

Separated into unit tests and Selenium tests in `app/testing/unit` and `app/testing/selenium`.

By default, Chrome browser is used for UI testing, and the driver will be automatically downloaded. If you want to use headless mode, just uncomment the line `options.add_argument('--headless')` in `base_test.py`.

### Running Unit Tests

Navigate to the project's root directory, make sure your test environment is clean and ready. 

```bash
python -m unittest discover -s app/testing/unit
```

This command will discover and run all test files within the `app/testing/unit` directory.

### Running Selenium Tests

Navigate to the project's root directory

```bash
python -m unittest discover -s app/testing/ui
```

This will discover and run all test files in the `app/testing/selenium` directory.

### UI Tests (Selenium)
- TestAuthFlows.test_successful_user_signup: Tests user signup flow, flash message, and login redirect.
- TestAuthFlows.test_successful_user_login_and_logout: Tests login with valid credentials and logout redirect.
- TestAuthFlows.test_user_login_with_invalid_credentials: Tests login failure with invalid credentials.
- TestUIDataImport.login_user: Logs in an existing user via UI for data import tests.
- TestUIDataImport.test01_create_tournament_with_valid_csv: Tests valid CSV upload via create tournament UI and database inserts.
- TestUIDataImport.test02_create_tournament_with_invalid_csv: Tests invalid CSV upload handling on create tournament UI.
- TestNavigation.test_public_page_accessibility_anonymous: Verifies anonymous access to public pages.
- TestNavigation.test_authenticated_page_access_and_redirects: Verifies redirects to login for unauthenticated users accessing protected pages.
- TestNavigation.test_404_error_page: Verifies the custom 404 error page displays correctly.

### Unit Tests
- TestForms.test_signup_form_valid: Make sure that signup form accepts valid input.
- TestForms.test_signup_duplicate_username: Ensures signup form rejects duplicate username.
- TestForms.test_signup_duplicate_email: Ensures signup form rejects duplicate email.
- TestForms.test_signup_password_mismatch: Ensures signup form rejects mismatched passwords.
- TestForms.test_login_form_valid: Validates login form accepts correct credentials.
- TestForms.test_create_tournament_valid: Make sure create tournament form with proper data.
- TestForms.test_create_tournament_missing_fields: Ensures create tournament form rejects missing required fields.
- TestForms.test_password_hashing: Verifies user password is hashed and verified correctly.
- TestDataImport.test_valid_csv_import: Tests CSV import function with a valid file, checking database records.
- TestDataImport.test_invalid_csv_import: Tests CSV import function raises exception on invalid file and form validation.