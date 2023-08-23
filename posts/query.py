import graphene
from graphql import GraphQLError
from .schema import PostType, LikeType, CommentType
from .models import Post, Like, Comment

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
    comment = graphene.Field(CommentType)
    
    def mutate(self, info, tweet):
        if not info.context.user.is_anonymous:
            new_post = Comment(post=tweet, created_by=info.context.user)
            new_post.save()
            return CreatePost(ok=True, post=new_post)
        raise GraphQLError('You are not authenticated. Log in')
    
class CreateComment(graphene.Mutation):
    class Arguments:
        comment = graphene.String(required=True)
        post_id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    comment = graphene.Field(CommentType)
    
    def mutate(self, info, post_id, comment):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('This post does not exist')
        if not info.context.user.is_anonymous:
            new_comment = Comment(comment=comment, created_by=info.context.user, post=post)
            new_comment.save()
            return CreateComment(ok=True, comment=new_comment)
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
    message = graphene.String()

    def mutate(self, info, like):
        try:
            liked = Like.objects.get(id=like)
        except Like.DoesNotExist:
            raise GraphQLError('You have not liked such post')
        
        if not info.context.user.is_anonymous:
            if liked.liked_by != info.context.user:
                liked.unlike()
                return UnLike(ok=True, message='You have unliked this post')
            raise GraphQLError('You are not authorised')
        raise GraphQLError('You are not authenticated')
    
class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        post = graphene.String(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id, post):
        updated_post = Post.objects.get(id=id)
        if updated_post.created_by != info.context.user:
            updated_post.post = post
            updated_post.save()
            return UpdatePost(ok=True, post=updated_post)
        raise GraphQLError('You are not authorised')
    
class UpdateComment(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        comment = graphene.String(required=True)
    
    ok = graphene.Boolean()
    comment = graphene.Field(CommentType)
    
    def mutate(self, info, id, comment):
        updated_comment = Comment.objects.get(id=id)
        if updated_comment.created_by != info.context.user:
            updated_comment.comment = comment
            updated_comment.save()
            return UpdateComment(ok=True, comment=updated_comment)
        raise GraphQLError('You are not authorised')
        
    
class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError('Post does not exist')
        if post.created_by != info.context.user:
            post.delete()
            return DeletePost(ok=True, post=post)
        raise GraphQLError('You are not authorised')
    
class DeleteComment(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    comment = graphene.Field(CommentType)
    
    def mutate(self, info, id):
        try:
            comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            raise GraphQLError('Comment does not exist')
        if comment.created_by != info.context.user:
            comment.delete()
            return DeleteComment(ok=True, comment=comment)
        raise GraphQLError('You are not authorised')
    
        
    

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    like_post = CreateLike.Field()
    unlike_post = UnLike.Field()
    

schema = graphene.Schema(query=Query, mutation=Mutation)
