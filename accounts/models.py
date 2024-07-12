import jwt
import uuid
from decouple import config
from datetime import datetime, timedelta

from django.db import models
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _



# Create your models here.
class CustomManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        
        user = self.model(email = self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("is_staff must value to True")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superuser must value to True")
        
        return self.create_user(self, email, password, **extra_fields)


class Organisation(models.Model):
    orgId = models.AutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=True, max_length=100)
    
    def __str__(self):
        return f"{self.orgId} {self.name} {self.description}"
    

class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    
    userId = models.AutoField(primary_key=True)
    firstName = models.CharField(blank=False, max_length=100) 
    lastName = models.CharField(blank=False, max_length=100)
    email = models.CharField(
        unique=True, 
        blank=False, 
        max_length=100,
        validators=[username_validator],
        error_messages={
            'unique': _("Email already exists")
        }
        )
    password = models.CharField(blank=False, max_length=100)
    phone = models.CharField(blank=True, max_length=100)
    organisation = models.ManyToManyField(Organisation)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']
    
    objects = CustomManager()
    
    
    def __str__(self) :
        return f"{self.userToken} {self.userId} {self.firstName} {self.lastName}  {self.email} {self.phone} "
    
    #Supposed to attach a token to the user.
    @property
    def userToken(self):
        token = jwt.encode(
            {'userId': self.userId,
             'firstName': self.firstName, 
             'lastName': self.lastName,
             'email': self.email,
             'phone':self.phone,
             'exp': datetime.now() + timedelta(minutes=8),
            },
            config("JWT_SECRET_KEY"),
            algorithm='HS256'
        )
        return token

    