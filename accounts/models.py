from django.contrib.auth.models import AbstractUser
from .maneger import CostumUserMeneger
from django.db import models
import uuid



class CostumUser(AbstractUser):

    email = models.EmailField(max_length=245,unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CostumUserMeneger()

    def __str__(self):
        return self.email


class EmailConfirmed(models.Model):
    user = models.OneToOneField(CostumUser,on_delete=models.CASCADE)
    token = models.URLField(default=uuid.uuid4)
  

