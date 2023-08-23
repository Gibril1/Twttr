import graphene
from graphql import GraphQLError
from .schema import PostType, LikeType
from .models import Post, Like

class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id= graphene.Int())

    def resolve_posts(self, info, **kwargs):
        return Post.objects.all()
    
    def resolve_post(self, info, id):
        return Post.objects.get(id=id)
    
class CreatePost(graphene.Mutation):
    class Arguments:
        tweet = graphene.String(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, tweet):
        if not info.context.user.is_anonymous:
            new_post = Post(post=tweet, created_by=info.context.user)
            new_post.save()
            return CreatePost(ok=True, post=new_post)
        raise GraphQLError('You are not authenticated. Log in')

class CreateLike(graphene.Mutation):
    class Arguments:
        post = graphene.Int(required=True)

    ok = graphene.Boolean()
    like = graphene.Field(LikeType)

    def mutate(self, info, post):
        try:
            liked_post = Post.objects.get(id=post)
        except Post.DoesNotExist:
            raise GraphQLError('Such post does not exist')
        
        if not info.context.user.is_anonymous:
            if not Like.objects.filter(liked_by=info.context.user,post=liked_post).exists():
                new_like = Like(liked_by=info.context.user, post=liked_post)
                new_like.save()
                return CreateLike(ok=True, like=new_like)
        raise GraphQLError('You are not authenticated')
    
class UnLike(graphene.Mutation):
    class Arguments:
        like = graphene.Int(required=True)

    ok = graphene.Boolean()
    

    def mutate(self, info, like):
        try:
            liked = Like.objects.get(id=like)
        except Like.DoesNotExist:
            raise GraphQLError('You have not liked such post')
        
        if not info.context.user.is_anonymous:
            if liked.liked_by != info.context.user:
                liked.unlike()
                return UnLike(ok=True)
            raise GraphQLError('You are not authorised')
        raise GraphQLError('You are not authenticated')
    
class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        tweet = graphene.String(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id, tweet):
        updated_post = Post.objects.get(id=id)
        if updated_post.created_by != info.context.user:
            updated_post.post = tweet
            updated_post.save()
            return UpdatePost(ok=True, post=updated_post)
        raise GraphQLError('You are not authorised')
        
    
class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id):
        if updated_post.created_by != info.context.user:
            updated_post = Post.objects.get(id=id)
            updated_post.delete()
            return DeletePost(ok=True, post=updated_post)
        raise GraphQLError('You are not authorised')
        
    

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    like_post = CreateLike.Field()
    unlike_post = UnLike.Field()
    

schema = graphene.Schema(query=Query, mutation=Mutation)
