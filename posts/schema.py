import graphene
from graphene_django import DjangoObjectType
from .models import Post, Like, Comment, Repost, Notifications



class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "comment", "created_at", "updated_at", "comment_by", "post")


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ("id", "liked_by", "post")

class RepostType(DjangoObjectType):
    class Meta:
        model = Repost
        fields = ("id", "comment", "post", "repost_by")

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notifications
        fields = ("id", "message")



class PostType(DjangoObjectType):
    like_count = graphene.Int()
    comment_count = graphene.Int()
    repost_count = graphene.Int()
    comments = graphene.List(CommentType)
    reposts = graphene.List(RepostType)

    def resolve_like_count(self, info):
        return self.like_count()
    
    def resolve_comment_count(self, info):
        return self.comment_count()
    
    def resolve_repost_count(self, info):
        return self.repost_count()
    
    def resolve_reposts(self, info):
        return self.reposts()
    
    def resolve_comments(self, info):
        return self.comments()

    class Meta:
        model = Post
        fields = ("id", "post", "created_at", "updated_at", "like_count", "comment_count", "created_by", "repost_count")



    