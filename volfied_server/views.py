from django.shortcuts import render
from game import Round
from volfied_server.enemy import Enemy


def game_view(request):
    enemies = [
        Enemy(radius=3, image='', speed=0.5),
    ]
    request.session['round'] = Round(100, 100, None, None, 0.8, enemies)
    return render(request, 'game.html', {"foo": "bar"},
                  content_type="html")
