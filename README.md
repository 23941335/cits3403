# CITS3403 Group Project

## Source
https://github.com/23941335/cits3403.git

## Description
This project is a web application for creating and managing tournaments for the game _Marvel Rivals_. Users can create their own tournaments and upload data as a CSV file collected from games played by tournament participants. They can add all the data from a tournament at once, if entering it after it is completed, or update the tournament data across multiple uploads as the tournament progresses in real time.

The tournament owner can set the tournament as either public or private. Public tournaments are accessible to all site visitors, while private tournaments are only accessible to people invited by the owner. Users can search for public tournaments and see a list of all tournaments they created or that have been shared with them.

Based on the uploaded data, we then provide uses with a variety of ways to view their team or individual performances in the tournament, with numerous metrics and visualisations to bring the make the data easy to understand and to be able to find useful insights quickly. To make it easier for users to upload data, we have a guide page which explains the format of the CSVs and allows them to download templates and examples.

## Implementation
The project is implemented using a Python Flask backend, connected to a SQLite3 database (via SQLAlchemy), and makes use of server side rendering to give users a customised experience depending on if they are logged in or not. We also have used AJAX to implement the search functionality to query the database for tournaments with matching names.

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

#### Virtual Environment:
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
#### Build the Database:
```
flask db upgrade
python seed.py
```
#### Start the Server:
```
flask run
```

#### Python Package Dependencies
- [email_validator](https://github.com/JoshData/python-email-validator)
- [Flask](https://github.com/pallets/flask)
- [Flask-Login](https://github.com/maxcountryman/flask-login)
- [Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)
- [Flask-SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy/)
- [Flask-WTF](https://github.com/pallets-eco/flask-wtf/)

Any other requirements listed in the requirements.txt are dependencies of these packages.

## Testing

Note: Selenium testing requires that you have Google Chrome installed, and that you have followed the setup instructions above.

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

## Sample Data

This sample data was provided in the app.db file in the project submission.

### Users
```
Username: test_user_1
Email: test_user_1@foo.foo
Has pfp
```
```
Username: test_user_2
Email: test_user_2@foo.foo
```
```
Username: test_user_3
Email: test_user_3@foo.foo
```
```
Username: test_user_4
Email: test_user_4@foo.foo
```
```
Username: test_user_5
Email: test_user_5@foo.foo
```
#### All users
```
Password: 12345678
```
### Tournaments
```
Name: test_user_1_private_unshared
Visibility: Private
Shared: None
```
```
Name: test_user_1_public_1
Visibility: Public
Shared: N/A
```
```
Name: test_user_2_private_shared
Visibility: Private
Shared: test_user_1
```
```
Name: test_user_1_public_2
Visibility: Public
Shared: N/A
```