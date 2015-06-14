# Volfied

Classic arcade game remake
Implemented as separate server (Django) and client (JS) apps


## Requirements
Project requires Python 2.7.9 to run
File requirements.txt contains all the requirements.

I used gevent-socketio for messaging. This package requires some outdated versions of Django and gevent lib,
so I recommend using virtualenv

Installing gevent might be tricky, it requires libevent source. It can be downloaded from the official site 
and the directory must be provided as an argument to gevent setup script


### Running project
Volfied server can be started by running
```
manage.py runserver_socketio
```
This starts the server on localhost:9000, so you can open this address in your browser
The project was developed and tester using Chrome (v43)


## Technical details

* **volfied_server** django app has all the game logic and server-client messaging
  * **algorithm.py** core geometry and volfied gameplay functions
  * **round.py** provides a class for managing a single round of the game
  * **event.py** contains all client-server messaging logic. it also has main game loop

* **Volfied/static/js/game.js** javascript client implementation that renders the game and provides input


Every frame js client collects the input (arrow keys state) from the user and send it via network as JSON.
On the server side each client has a round attached to session. The round calculates its next state based on previous
state and input. The next state is then transmitted back to client (JSON)
