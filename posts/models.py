from django.db import models

# Create your models here.
class Post(models.Model):
    post = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.post