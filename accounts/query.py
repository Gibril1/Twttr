import graphene
import graphql_jwt
from graphql import GraphQLError
from .schema import UserType, FollowingType
from .models import Following, User
from posts.models import Post, Comment, Repost, Notifications
from posts.schema import PostType, CommentType, RepostType, NotificationType

class Query(graphene.ObjectType):
    # users
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info, **kwargs):
        return User.objects.all()
    
    def resolve_me(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in!')
        return info.context.user
    
    # following and following
    followers = graphene.List(UserType)
    following = graphene.List(UserType)

    def resolve_followers(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        followers = Following.objects.filter(following=info.context.user)
        return User.objects.filter(username__in=[follower.follower for follower in followers])
    
    def resolve_following(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        following_users = Following.objects.filter(follower=info.context.user)
        return User.objects.filter(username__in=[follow.following for follow in following_users])
    
    # posts, reposts and comments the user has made
    user_posts = graphene.List(PostType)
    user_comments = graphene.List(CommentType)
    user_reposts = graphene.List(RepostType)

    def resolve_user_posts(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        return Post.objects.filter(created_by=info.context.user)
    
    def resolve_user_comments(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        return Comment.objects.filter(created_by=info.context.user)
    
    def resolve_user_reposts(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        return Repost.objects.filter(created_by=info.context.user)
    
    # notifications
    notifications = graphene.List(NotificationType)
    def resolve_notifications(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        return Notifications.objects.filter(message_for=info.context.user)
    
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
        notification = Notifications(
                    message = f'{info.context.user.username} followed you!',
                    message_for = user
                )
        notification.save()
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
