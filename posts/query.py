import graphene
from django.db.models import Q
from graphql import GraphQLError
from .schema import PostType, LikeType, CommentType, RepostType
from .models import Post, Like, Comment, Repost, Notifications

class Query(graphene.ObjectType):
    # posts
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id= graphene.Int())
    search_post = graphene.List(PostType, search=graphene.String())
    def resolve_posts(self, info, **kwargs):
        return Post.objects.all()

    def resolve_post(self, info, id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        return Post.objects.get(id=id)
    
    def resolve_search_post(self, info, search=None):
        if search:
            filter = Q(post__icontains=search)
            return Post.objects.filter(filter)
        
    # comments
    comments = graphene.List(CommentType)
    comment = graphene.Field(CommentType, id= graphene.Int()) 
    def resolve_comments(self, info, **kwargs):
        return Comment.objects.all()
    
    def resolve_comment(self, info, id):
        return Comment.objects.get(id=id)
    
    # reposts
    reposts = graphene.List(RepostType)
    repost = graphene.Field(RepostType, id= graphene.Int())

    def resolve_reposts(self, info, **kwargs):
        return Repost.objects.all()
    
    def resolve_repost(self, info, id):
        return Repost.objects.get(id=id)
    
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
    
class CreateComment(graphene.Mutation):
    class Arguments:
        comment = graphene.String(required=True)
        post_id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    comment = graphene.Field(CommentType)
    
    def mutate(self, info, post_id, comment):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('This post does not exist')
        
        # Comment On A Post
        new_comment = Comment(comment=comment, comment_by=info.context.user, post=post)
        new_comment.save()
        notification = Notifications(
                    message = f'{info.context.user.username} commented on your post',
                    message_for = post.created_by
                )
        notification.save()
        return CreateComment(ok=True, comment=new_comment)
        

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
                notification = Notifications(
                    message = f'{info.context.user.username} liked your post',
                    message_for = liked_post.created_by
                )
                notification.save()
                return CreateLike(ok=True, like=new_like)
            raise GraphQLError('You cannot like a single post twice')
        raise GraphQLError('You are not authenticated')
    
class UnLike(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, post_id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authorized')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('Such post does not exist')
        
        liked_post = Like.objects.filter(post=post, liked_by=info.context.user).first()
        if liked_post:
            liked_post.unlike()
        else:
            return GraphQLError('You have not liked such a post')
        return UnLike(ok=True, message='You have unliked the post')

class CreateRepost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)
        comment = graphene.String()
    
    ok = graphene.Boolean()
    repost = graphene.Field(RepostType)
    message = graphene.String()
    

    def mutate(self, info, post_id, comment):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authorised')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('Such post does not exist')
        
        repost = Repost(
            repost_by = info.context.user,
            post = post,
            comment = comment
        )
        notification = Notifications(
                    message = f'{info.context.user.username} shared your post',
                    message_for = post.created_by
                )
        notification.save()
        repost.save()
        return CreateRepost(ok=True, repost=repost, message='You have successfully reposted this post!')
        
    
class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        post = graphene.String(required=True)
    
    ok = graphene.Boolean()
    post = graphene.Field(PostType)
    
    def mutate(self, info, id, post):
        updated_post = Post.objects.get(id=id)
        if updated_post.created_by == info.context.user:
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
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated')
        try:
            updated_comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            raise GraphQLError('Such a comment does not exist')
        
        if updated_comment.comment_by == info.context.user:
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
        if post.created_by == info.context.user.id:
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
        if comment.comment_by == info.context.user:
            comment.delete()
            return DeleteComment(ok=True, comment=comment)
        raise GraphQLError('You are not authorised')
    

class DeleteRepost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        try:
            repost = Repost.objects.get(id=id)
        except Repost.DoesNotExist:
            raise GraphQLError('Repost does not exist')

        if repost.repost_by == info.context.user:
            repost.delete()
            return DeleteRepost(ok=True, message='Repost has been deleted') 
        raise GraphQLError('You are not authorized to delete this')

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    like_post = CreateLike.Field()
    unlike_post = UnLike.Field()
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()
    repost = CreateRepost.Field()
    delete_repost = DeleteRepost.Field()
    

schema = graphene.Schema(query=Query, mutation=Mutation)
