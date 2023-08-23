import graphene
from graphql import GraphQLError
from .schema import PostType
from .models import Post

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
        new_post = Post(post=tweet)
        new_post.save()
        return CreatePost(ok=True, post=new_post)
    
class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        tweet = graphene.String(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id, tweet):
        updated_post = Post.objects.get(id=id)
        updated_post.post = tweet
        updated_post.save()
        return UpdatePost(ok=True, post=updated_post)
    
class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id):
        updated_post = Post.objects.get(id=id)
        updated_post.delete()
        return DeletePost(ok=True, post=updated_post)
    

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    

schema = graphene.Schema(query=Query, mutation=Mutation)
