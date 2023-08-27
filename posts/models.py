from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    
    def like_count(self):
        return Like.objects.filter(post=self).count()
    
    def comment_count(self):
        return Comment.objects.filter(post=self).count()
    
    def repost_count(self):
        return Repost.objects.filter(post=self).count()
    


    
class Like(models.Model):
    liked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def unlike(self):
        self.delete()
    
    
    def __str__(self) -> str:
        return self.post.post  
      
    class Meta:
        unique_together = ('liked_by', 'post')

class Comment(models.Model):
    comment_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self) -> str:
        return self.comment
    
class Repost(models.Model):
    repost_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self) -> str:
        return self.comment
    
