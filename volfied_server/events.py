import json

__author__ = 'Alex'

from django_socketio import events

@events.on_message(channel="echo")
def message(request, socket, context, msg):
    obj = json.loads(msg)

    dx, dy = 0, 0
    if obj['up']:
        dy += -10
    if obj['down']:
        dy += 10
    if dy == 0:
        if obj['left']:
            dx += -10
        if obj['right']:
            dx += 10

    request.session['x'] += dx
    request.session['y'] += dy

    new_pos = {'x': request.session['x'], 'y': request.session['y']}
    socket.send(json.dumps(new_pos))

@events.on_connect
def connect(request, socket, context, *args):
    pass

@events.on_subscribe(channel="echo")
def connect(request, socket, context, *args):
    print request.session