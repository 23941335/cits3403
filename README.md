# CITS3403 Group Project

## Description

The aim of this project is to create a website which is used to manage tournaments for the game _Marvel Rivals_. Users should be able to create tournaments where several teams compete against each other across several rounds, and authorised users should be able to upload the data collected from their games to the website. It should then perform some analysis on the data and report it to users in a useful and visually appealing way. Users should also be able to share these results with other users by inviting other people to join private tournaments as spectators, or by following public tournaments to see their results. 

TODO: ensure above fulfills: "a description of the purpose of the application, explaining its design and use."

## Contributors
| Student Number | Name            | GitHub Username |
|----------------|-----------------|-----------------|
| 23941335       | George Brice    | 23941335        |
| 22666335       | Koda(Zhengxun) Lan        | Kod4-lan        |
| 23769985       | Max Moltoni     | SuperMax732     |
| 24240636       | Dongkai Liu Liu | itchat          |

## Planning and Meeting Notes
https://github.com/23941335/cits3403/blob/main/planning.md

## Setup

### Instructions

Set up virtual environment and install requirements:
```
python -m venv .venv
source .venv/*/activate
pip install -r requirements.txt
```
Set the environment variables:
```
export SECRET_KEY='somevaluehere'
```
Build the database:
```
flask db upgrade
python seed.py
```
Start the server:
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

#### Create Virtual Environment and Install Dependencies

1. `python -m venv .venv`
2. `source .venv/bin/activate` (Linux/MacOS); or `.venv\Scripts\activate` (Windows); or `source .venv/Scripts/activate` (WSL)
3. `pip install -r requirements.txt`

If you want to delete the .venv:
`rd /s /q .venv` on Windows or
`rm -rf .venv` on Linux/MacOS

#### Database
<!-- 
Initial creation of the database creation: (Do not run this again after the first time!)
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
``` 
-->

If you do not yet have th app.db file (the database), run:
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
