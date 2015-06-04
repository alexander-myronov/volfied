from django.shortcuts import render
from game import Round

def game_view(request):
    request.session['round'] = Round(100,100,None,None,0.8)
    return render(request, 'game.html', {"foo": "bar"},
                  content_type="html")
