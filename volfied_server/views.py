import random
from django.shortcuts import render
from round import Round
from volfied_server.UserContext import UserContext
from volfied_server.enemy import Enemy



def game_view(request):

    if 'context' in request.session:
        ctx = request.session['context']
    else:
        ctx = UserContext()
        request.session['context'] = ctx

    request.session['round'] = Round.get_round(ctx.round)
    return render(request, 'game.html', {}, content_type="html")
