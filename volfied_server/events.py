"""
server request-response logic
server gets controls from client
and sends back new game state, based on controls
"""
import json
from volfied_server.round import Round
from django_socketio import events


@events.on_message(channel="echo")
def message(request, socket, context, msg):
    """function called when message is received"""
    obj = json.loads(msg)

    round = request.session['round']

    ctx = request.session['context']
    if ctx.lives < 0:
        return

    if ctx.win:
        return

    add_score, dead = round.tick(obj)
    response = round.get_response()

    ctx.score += add_score
    response['score'] = ctx.score

    if round.is_completed():
        ctx.round += 1  # nextround
        try:
            r = Round.get_round(ctx.round)
            request.session['round'] = r
            r.start()
            response = r.get_init_message()
        except:
            response['status'] = 1
            ctx.win = True

        socket.send(json.dumps(response))

    if dead:
        ctx.lives -= 1
    if ctx.lives < 0:
        response['status'] = -1

    response['lives'] = ctx.lives
    response['score'] = ctx.score

    response['cmd'] = 'tick'

    socket.send(json.dumps(response))


@events.on_connect
def connect(request, socket, context, *args):
    pass


@events.on_subscribe(channel="echo")
def subscribe(request, socket, context, *args):
    """function called when a client subscribed to channel 'echo'"""
    r = request.session['round']
    r.start()
    response = r.get_init_message()
    socket.send(json.dumps(response))
