import json

__author__ = 'Alex'

from django_socketio import events

@events.on_message(channel="echo")
def message(request, socket, context, msg):
    obj = json.loads(msg)

    round = request.session['round']

    round.tick(obj)

    response = round.get_response()

    socket.send(json.dumps(response))

@events.on_connect
def connect(request, socket, context, *args):
    pass

@events.on_subscribe(channel="echo")
def connect(request, socket, context, *args):
    request.session['round'].start()