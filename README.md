# CITS3403 Group Project

## Description

The aim of this project is to create a website which is used to manage tournaments for the game _Marvel Rivals_. Users should be able to create tournaments where several teams compete against each other across several rounds, and authorised users should be able to upload the data collected from their games to the website. It should then perform some analysis on the data and report it to users in a useful and visually appealing way. Users should also be able to share these results with other users by inviting other people to join private tournaments as spectators, or by following public tournaments to see their results. 

## Planning and Meeting Notes
https://github.com/23941335/cits3403/blob/main/planning.md

## Setup

### Backend

#### Python Package Dependencies
- [Flask](https://github.com/pallets/flask)
    - [Jinja](https://github.com/pallets/jinja) (bundled with Flask)
- [Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)
- [Flask-SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy/)
- [Flask-WTF](https://github.com/pallets-eco/flask-wtf/) <!-- cf. lecture 9, slide 31 -->
Any other requirements listed in the requirements.txt are dependencies of these packages.
<!-- ```pip install flask flask-sqlalchemy flask-migrate flask-wtf``` -->

#### Create Virtual Environment and Install Dependencies

1. `python -m venv .venv`
2. `source .venv/bin/activate` (Linux/MacOS); or `.venv\Scripts\activate` (Windows); or `source .venv/Scripts/activate` (WSL)
3. `pip install -r requirements.txt`

If you want to delete the .venv:
`rd /s /q .venv` on Windows or
`rm -rf .venv` on Linux/MacOS
