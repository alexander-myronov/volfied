import random
from django.shortcuts import render
from game import Round
from volfied_server.enemy import Enemy


def game_view(request):
    enemies = []
    for i in xrange(5):
        enemies.append(Enemy(radius=random.randrange(3,6), image='', speed=random.randrange(1,3)))
    request.session['round'] = Round(100, 100, None, None, 0.8, enemies)
    return render(request, 'game.html', {"foo": "bar"},
                  content_type="html")
