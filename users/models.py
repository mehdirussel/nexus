from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class NexusUser(AbstractUser):
  # tous les labels sont vides, on n'utilise que les placeholders
  username = models.CharField(max_length = 50, unique = True)
  photo_de_profil = models.ImageField(default='default.jpg', upload_to='user_imgs',null=True,blank=True)
  email = models.EmailField(unique = True)


  def __str__(self):
    return f' |{self.username}--{self.email}|'
