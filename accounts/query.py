import graphene
import graphql_jwt
from graphql import GraphQLError
from .schema import UserType
from django.contrib.auth.models import User

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info, **kwargs):
        return User.objects.all()
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Not logged in!')
        return user

class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)
    
    ok = graphene.Boolean()
    user = graphene.Field(UserType)
    message = graphene.String()

    def mutate(self, info, username, email, password, password2):
        if password != password2:
            return RegisterUser(ok=False, user=None, message='Passwords do not match')
        
        user = User(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        return RegisterUser(ok=True, user=user, message=f'Account has been successfully created for {username}')

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
