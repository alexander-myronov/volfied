from django.shortcuts import render


def game_view(request):
    request.session['x'] = 50
    request.session['y'] = 50
    return render(request, 'game.html', {"foo": "bar"},
                  content_type="html")
