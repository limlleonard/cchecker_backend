# Chinese Checker Backend
## Description
[Link to play the game](https://cchecker-frontend-stateless.onrender.com/)

[Link to frontend code](https://github.com/limlleonard/cchecker_frontend)

Chinese Checker is a popular strategy board game in China, it was also my favorite game in my school time. It can be played by 1-6 person. The player try to move all the 10 pieces to the opposite corner of the board. One piece could be moved to an adjacent field or jump over ONE other piece once or for more times, but not jump over more than one piece.

<img src="./img/cchecker4.png" alt="screenshot" width="70%"/>

## Play
Start: It will start a new game from the beginning. Old data saved with the same roomnr will be deleted.

Load / Join: It will load a saved game or join the game.

Reset: It will reset the game and delete the record.

Room info: It shows game state saved in database

`<<<`: One step backward

`>>>`: One step forward

## Installation
(You have to start both servers of frontend and backend to test the game locally)

Clone repo

`git clone https://github.com/limlleonard/cchecker_backend.git`

Install requirements

`pip install -r requirements.txt`

Change the Database to local database

`DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}`

Make migrations and migrate

`python manage.py makemigrations`

`python manage.py migrate`

Start the server

`python manage.py runserver`

This start up the api server. In order to play the game, start the server in the frontend by following the instructions

## Features
By using WebSocket and Djanog Channels, you could play the game with friends remotely

## Components
Frontend is built by React. Backend is built by Django.

### Database
Django ORM is used to interact with database.
- GameStateEnd: keep track of the end state of a game (used in the old version of the game)
- GameStateTemp: keep track of (only) the last move or select of the player
- Moves: keep track of all the moves. With those moves, the current state can be calculated by adding up all the moves to the initial state 

### Coordinate system
Defining each position of the board is a little tricky. They are defined by three numbers.
- First number defines to which direction it goes away from the center. There are six possible directions.
- Second number defines how far it goes away from the center
- Third number defines how far it goes after turning right

The coordinate of the blue point would be (1,3,2)

<img src="./img/sternhalma3.png" alt="defining board" width="60%"/>
