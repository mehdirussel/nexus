from django.db import models
from django.contrib.auth.models import User,Group

# Create your models here.

class Utilisateur(User):
    r = 0

class GroupeUtilisateurs(Group):
    r = 0

class SalonDiscussion(models.Model):
    r = 0