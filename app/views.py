# Create your views here.
import json
from django.core.urlresolvers import reverse
from pip import status_codes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.core.cache import get_cache
from app.models import Player, PlayerAction, User, UserPlayer, UserScore
from rest_framework import status
from app.forms import SelectUsername
from django.shortcuts import redirect

def index(request):
    """
    HTML access point.
    The internal navigation and rendering is performed with backbone.
    """
    return render_to_response('index.html')

def data(request):
    """
    HTML access point.
    Manages the live data feed. If there is data on render, it will redirect to clear the data.
    """
    if Player.objects.count()>0:
        return redirect(reverse("clean"))
    return render_to_response("data.html")

@api_view(['GET'])
def players(request):
    """
    Returns the results in the current match. Will check for cached result before calculation. The cache is invalidated
     on recorded action.
    """
    cache = get_cache('default')
    players = cache.get("players")
    if not players:
        players = Player.get_results()
        cache.set('players', players)
    return Response(players)

@api_view(["GET"])
def users(request):
    """
    Returns the results of the users in the current match. Will check for cache before calculation.
    """
    cache= get_cache("default")
    users = cache.get('users')
    if not users:
        users = User.get_results()
        cache.set('users', users)
    return Response(users)

@api_view(["POST"])
def record_action(request):
    """
    Records a match event. After recording, reset the cache.
    The post arguments are team, name, action, seconds_in_game
    """
    #todo defensive for wrong post data
    name = request.POST.get("name")
    team = request.POST.get("team")
    action = request.POST.get("action")
    seconds_in_game = request.POST.get("seconds_in_game")

    #get or create the player
    player, created = Player.objects.get_or_create(
        name=name,
        team=team
    )

    #create the action
    action = PlayerAction.objects.create(
        player=player,
        type=action,
        seconds_in_game=seconds_in_game
    )

    #create the scoring for users
    affected_users = [up['user'] for up in UserPlayer.objects.filter(player=player).values('user')]
    userscores= []
    for user_id in affected_users:
        userscore = UserScore(
            playeraction=action,
            user_id=user_id
        )
        userscores.append(userscore)
    UserScore.objects.bulk_create(userscores)

    #reset the cache
    cache= get_cache('default')
    players = Player.get_results()
    cache.set('players', players)

    users = User.get_results()
    cache.set("users", users)
    return Response({'success':True})

def clean(request):
    """
    Cleans all the match specific data. Will not remove the users and their nicknames. Invalidates the caches.
    """
    Player.objects.all().delete()
    cache = get_cache("default")
    cache.delete("players")
    cache.delete('users')
    return redirect(reverse("data"))


def join(request):
    """
    HTML endponing.
    Supply your username.
    """
    form = SelectUsername(request.POST or None)
    if form.is_valid():
        u=User.objects.create(
            name = form.cleaned_data["name"]
        )
        request.session['username']=u.name
        request.session['uid']=u.id
        response = render_to_response("join.html", {'success':True})
        return response
    else:
        return render_to_response("join.html", {"form":form})

@api_view(["POST"])
def selectplayer(request):
    """
    Select a player to add to your selection.
    """
    #select user
    if "uid" not in request.session:
        return Response({"success":False, 'message':"Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    user = User.objects.get(pk=request.session['uid'])

    #make sure he has a slot
    if UserPlayer.objects.filter(user=user).count()>=3:
        return Response({'success':False, "message":"You don't have an empty slot"})

    #select player
    player_id = request.POST.get("player")
    player = Player.objects.get(pk=player_id)

    #add the player to selection
    userplayer = UserPlayer.objects.get_or_create(
        user= user,
        player=player
    )
    return Response({'success':True})

@api_view(["POST"])
def dropplayer(request):
    """
    Drop a player from your selection
    """

    #select user
    if "uid" not in request.session:
        return Response({"success":False, 'message':"Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    user = User.objects.get(pk=request.session['uid'])

    #remove the selection
    player_id = request.POST.get("player")
    UserPlayer.objects.filter(user=user, player_id=player_id).delete()
    return Response({'success':True})

@api_view(["GET"])
def currentplayers(request):
    """
    Returns the players you are currently playing with.
    """
    if "uid" not in request.session:
        return Response({"success":False, 'message':"Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    user = User.objects.get(pk=request.session.get("uid"))
    players = [up.player for up in UserPlayer.objects.filter(user=user).select_related("player")]
    players = [{'name':p.name, "team":p.team, "id":p.id} for p in players]
    return Response(players)