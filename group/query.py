import graphene
from graphql import GraphQLError
from .schema import GroupType, GroupMembershipType
from .models import GroupMembership, Group

class Query(graphene.ObjectType):
    # groups
    groups = graphene.List(GroupType)
    group = graphene.Field(GroupType, id= graphene.Int())

    def resolve_groups(self, info, **kwargs):
        return Group.objects.all()
    
    def resolve_group(self, info, id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        try:
            return Group.objects.get(id=id)
        except Group.DoesNotExist:
            raise GraphQLError('Group does not exist')
        
    # group membership
    group_memberships = graphene.List(GroupMembershipType)
    group_member = graphene.Field(GroupMembershipType)

    def resolve_group_memberships(self, info, **kwargs):
        return GroupMembership.objects.all()


class CreateGroup(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
    
    ok = graphene.Boolean()
    group = graphene.Field(GroupType)
    message = graphene.String()

    def mutate(self, info, name):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Please log in')
        
        if Group.objects.filter(name=name).exists():
            raise GraphQLError('Someone has already taken this group name')
        
        group = Group(
            name=name,
            created_by=info.context.user
        )
        group.save()
        return CreateGroup(ok=True, group=group, message='You have successfully created a group')

class JoinGroup(graphene.Mutation):
    class Arguments:
        group_id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    group_membership = graphene.Field(GroupMembershipType)
    message = graphene.String()

    def mutate(self, info, group_id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GraphQLError('Group does not exist')
        
        membership = GroupMembership(
            group=group,
            user=info.context.user,
            status='Pending'
        )
        membership.save()
        return JoinGroup(ok=True, group_membership=membership, message='You have joined this group. Wait for approval')


class Mutation(graphene.ObjectType):
    create_group = CreateGroup.Field()
    join_group = JoinGroup.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
