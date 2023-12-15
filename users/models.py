from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class NexusUser(AbstractUser):
  # on veut que username soit unique
  username = models.CharField(max_length = 50, unique = True) 
  photo_de_profil = models.ImageField(default='default.jpg', upload_to='profile_pics')
  # utiliser login par email force a email d'etre unique
  USERNAME_FIELD = 'email'

  def __str__(self):
    return f' |{self.username}--{self.email}|'
