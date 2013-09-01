from django.db import models
from django.db.models.signals import pre_save


class Player(models.Model):
    """
    Football player model
    """
    name = models.CharField(max_length=150)
    team = models.CharField(max_length=150)

    @classmethod
    def get_results(cls):
        """
        Calculate the current result for the players.
        """
        #get all the players and their actions at once in order to save db load
        players = cls.objects.all()
        actions = PlayerAction.objects.values("player_id","score")

        #format the data in dictionary for faster access
        players_dict = dict(
            (p.id, {"id":p.id,'name':p.name, "team":p.team ,"score":0})
            for p in players
        )

        #attribute score to players
        for a in actions:
            player = players_dict[a['player_id']]
            player['score']+=a['score']

        players= players_dict.values()
        return players

class PlayerAction(models.Model):
    """
    Model storing all players action and the scores they bring.
    """
    player = models.ForeignKey(Player)
    seconds_in_game = models.IntegerField()
    type = models.CharField(max_length=150)
    score = models.IntegerField(default=0)


def player_action_pre_save(sender, instance,**kwargs):
    """
    Player action pre-save. Find the score for this particular action.
    """
    score = ACTION_SCORING.get(instance.type, 0)
    instance.score=score
pre_save.connect(player_action_pre_save, sender=PlayerAction)

class User(models.Model):
    """
    Simplified user model. The binding is stored in unsecure cookie.
    """
    name = models.CharField(max_length=150, unique=True, db_index=True)

    @classmethod
    def get_results(cls):
        """
        Get the top performing users.
        """
        #get all the users and their scores
        userscores = UserScore.objects.select_related("user", 'playeraction').all()

        #group userscores by user
        user_dict = {}
        for userscore in userscores:
            if userscore.user not in user_dict:
                user_dict[userscore.user]=[]
            user_dict[userscore.user].append(userscore.playeraction)

        #sum the scores
        for key, value in user_dict.items():
            user_dict[key]= sum((pa.score for pa in value))

        #add players with 0 result
        users = User.objects.all()
        for user in users:
            if user not in user_dict:
                user_dict[user]=0

        #format the result
        result = [{'username':user.name, 'uid':user.id, 'score':score} for user,score in user_dict.items()]
        return result

class UserPlayer(models.Model):
    """
    Model recording the players selected by the user.
    """
    user = models.ForeignKey(User, db_index=True)
    player = models.ForeignKey(Player)

class UserScore(models.Model):
    """
    Model saving the Player Action and as a consequence its score for a user. This is necessary as users can substitute
    players.
    """
    playeraction = models.ForeignKey(PlayerAction)
    user = models.ForeignKey(User)


ACTION_SCORING={
    "goal":20,
    "foul":-3,
    'goal assist':10,
    "gab":4,
    "shot missed": 3,
    'wfk':2,
    'corner conceded':-2,
    "yellow card":-8,
    'handball':-3,
    'own goal':-10
}