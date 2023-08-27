import graphene
from graphene_django import DjangoObjectType
from .models import User
from .models import Following

class UserType(DjangoObjectType):
    follower_count = graphene.Int()
    following_count = graphene.Int()

    def resolve_follower_count(self, info):
        return self.follower_count()
    
    def resolve_following_count(self, info):
        return self.following_count()

    class Meta:
        model = User
        fields = '__all__'

    

class FollowingType(DjangoObjectType):
    class Meta:
        model = Following
        fields = '__all__'


