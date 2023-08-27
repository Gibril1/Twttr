from django.db import models
from django.contrib.auth.models import AbstractUser as DefaultUser

# Create your models here.
class User(DefaultUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField()
    location = models.CharField(max_length=20)

    USERNAME_FIELD = 'username'

    def follower_count(self):
        return Following.objects.filter(following=self).count()
    
    def following_count(self):
        return Following.objects.filter(follower=self).count()
    
class Following(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_followed')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def unfollow(self):
        self.delete()