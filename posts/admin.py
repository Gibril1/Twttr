from django.contrib import admin
from .models import Post, Comment, Like, Notifications

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Notifications)
