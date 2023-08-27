import graphene
import graphql_jwt
from graphql import GraphQLError
from .schema import UserType, FollowingType
from .models import Following, User

class Query(graphene.ObjectType):
    # users
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info, **kwargs):
        return User.objects.all()
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Not logged in!')
        return user
    
    # following
    followers = graphene.List(FollowingType)
    
    def resolve_followers(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        return Following.objects.filter(following=info.context.user)

class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        bio = graphene.String()
        location = graphene.String()
    
    ok = graphene.Boolean()
    user = graphene.Field(UserType)
    message = graphene.String()

    def mutate(self, info, username, email, password, password2, **kwargs):
        if password != password2:
            raise GraphQLError('Passwords do not match')
        if User.objects.filter(username=username).filter(email=email).exists():
            raise GraphQLError('User with similar details already exist')
        user = User(
            username=username,
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return RegisterUser(ok=True, user=user, message=f'Account has been successfully created for {username}')
    
class FollowUser(graphene.Mutation):
    class Arguments:
        user_followed = graphene.Int(required=True)

    ok = graphene.Boolean()
    following = graphene.Field(FollowingType)
    message = graphene.String()

    def mutate(self, info, user_followed):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        try:
            user = User.objects.filter(id=user_followed).first()
        except User.DoesNotExist:
            raise GraphQLError('User does not exist')
        
        if Following.objects.filter(follower=info.context.user, following=user).exists():
            raise GraphQLError('You are already following')
        
        following_relationship  = Following(
            follower = info.context.user,
            following = user
        )
        following_relationship.save()
        return FollowUser(ok=True, following=following_relationship, message='You have followed this user')
    
class UnFollowUser(graphene.Mutation):
    class Arguments:
        user_followed = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, user_followed):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        try:
            user = User.objects.get(id=user_followed)
        except User.DoesNotExist:
            raise GraphQLError('User does not exist')
        try:
            following = Following.objects.get(following=user, follower=info.context.user)
            print('here')
            following.unfollow()
        except Following.DoesNotExist:
            raise GraphQLError('You are not following such user')
        return UnFollowUser(ok=True, message='You have unfollowed this user')
        

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnFollowUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
