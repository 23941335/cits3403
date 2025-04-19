# CITS3403 Group Project

## Planning and Meeting Notes
https://github.com/23941335/cits3403/blob/main/planning.md

## Setup

### Backend

#### Python Package Dependencies
- [Flask](https://github.com/pallets/flask)
    - [Jinja](https://github.com/pallets/jinja) (bundled with Flask)
- [Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)
- [Flask-SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy/)

Any other requirements listed in the requirements.txt are dependencies of these packages.
<!-- ```pip install flask flask-sqlalchemy flask-migrate``` -->
#### Create Virtual Environment and Install Dependencies

1. `python -m venv .venv`
2. `source .venv/bin/activate` (Linux/MacOS); or `.venv\Scripts\activate` (Windows); or `source .venv/Scripts/activate` (WSL)
3. `pip install -r requirements.txt`

If you want to delete the .venv:
`rd /s /q .venv` on Windows or
`rm -rf .venv` on Linux/MacOS