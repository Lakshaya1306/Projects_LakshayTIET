from django.db import models
from django.contrib.auth.models import  BaseUserManager, AbstractUser, PermissionsMixin


class user(AbstractUser, PermissionsMixin):
    contact = models.BigIntegerField(unique=True,null = True)
    DOB = models.DateField()
    
    USERNAME_FIELD = 'username'
    