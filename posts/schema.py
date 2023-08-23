import graphene
from graphene_django import DjangoObjectType
from .models import Post, Like, Comment

class PostType(DjangoObjectType):
    like_count = graphene.Int()

    def resolve_like_count(self, info):
        return self.like_count()

    class Meta:
        model = Post
        fields = ("id", "post", "created_at", "updated_at", "like_count", "created_by")

class CommentType(DjangoObjectType):

    class Meta:
        model = Comment
        fields = ("id", "comment", "created_at", "updated_at", "comment_by")


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ("liked_by", "post")