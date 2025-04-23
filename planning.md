# Features

## Core

### Users
- **User roles**
  - **Tournament creator/owner/manager**
    - Uploads the data
    - Can associate user accounts with player gamertags
  - **Participant**
  - **Guest**
- Login, password reset, etc.

### CSV file upload for data entry (or on web page?)
- Whole tournament

### Data Analysis
- **Game statistics**, K/D, compared to past performance
- **Tournament**
  - **Team**
    - Leaderboard
    - Performance in each game in tournament
  - **Player**
    - Leaderboard (team/tournament wide)
    - Performance in each game in tournament
- **All Time**
  - **Team**
    - Leaderboard
    - Statistics
  - **Player**
    - Leaderboard
    - Statistics

### Share data
- Public tournaments: anyone can see results/data analysis
- Participants and guests in private tournaments who are invited

## Ideal Features
- Likes and comments on tournament posts (?)
- Data analysis
  - Team/player stats comparison
- Requests to join/follow/view a private tournament

## Nice to Have
- Screenshot of scoreboard upload to extract data (via OCR)
- Share data – export to socials?
- Following tournaments, and notifications for new updates to them

# Database Format

**Note:** this is representative of the concepts and fields we store in the database, not necessarily the underlying logical structure. This is a higher abstraction, but the tables will be more normalised in the actual database.

_The database structure will be quite normalised (so there will be more tables than maybe is strictly necessary), but I think I will write some de-normalised views to make it easier for others to interact with it for read access, which will be most common for retrieving and displaying it to the front end._  

## Game Stats
- Teams Names
- Team players (need to record this unless we assume the same team always has same players which is not realistic, and is needed for good player-level stats recording)
- Winner
- MVP
- SVP
- Who won the medals
- Map played
- Gamemode

## Player Stats
- Player username
- Hero played
- Kills
- Deaths
- Assists
- Final Hits
- Damage
- Damage Blocked
- Healing
- Accuracy

## Users and Permissions

**Q: Do we want to record first / last name too?**

- Username
- Password (hashed, obviously)
- Email
- Account status (for disabling accounts etc. Do we want this feature?)
- User Role
  - Administrator (website admins)
  - Tournament Manager (creates tournaments and uploads data)
  - Participant (a person who is playing in the tournament)
  - Guest (someone invited to view a private tournament, but not playing in it)
- Account creation time


# Site Structure
(Notes based on issue #2)

The following pages fulfill the introductory view requirement, "describing the context and purpose of the application, and allowing the user to create an account or log in.".

- a homepage
- login page
- sign up page

Then for data upload:
- a page to set up tournaments and then the ability to add data to them. Probably this is one page.

For visualisation:
- player profile data page (e.g. something like /view/player?id=1234)
- tournament data page (e.g. /view/tournamnet?id=54)
- team data page (e.g. /view/team/teamnamehere or /view/team?id=11)
whether we can have all of these depends on if we get time to implement all of the different data views, but I think so. There might also be more ways to view the data.

For sharing:

Probably wouldnt be a totally separate page, more of a menu inside the tournamnet set up to invite other users. Would allow searching for users and adding them.
Another option would maybe allow for users to search for tournaments and follow them or request to join (as a guest/viewer) if private.

Other:

- user account settings page
- tournament feed (maybe?)
- possibly some admin only pages (if time permits)
