from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    post = models.TextField(null=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.post