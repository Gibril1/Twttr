import graphene
from graphql import GraphQLError
from .schema import GroupType, GroupMembershipType
from .models import GroupMembership, Group
from posts.models import Notifications

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
    group_membership = graphene.Field(GroupMembershipType, id= graphene.Int())

    def resolve_group_memberships(self, info, **kwargs):
        return GroupMembership.objects.all()


class CreateGroup(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
    
    ok = graphene.Boolean()
    group = graphene.Field(GroupType)
    message = graphene.String()

    def mutate(self, info, name, description):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Please log in')
        
        if Group.objects.filter(name=name).exists():
            raise GraphQLError('Someone has already taken this group name')
        
        group = Group(
            name=name,
            description=description,
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
        
        # check if user is already a member of the group
        check_membership = GroupMembership.objects.filter(group=group, user=info.context.user).first()
        if not check_membership:
            membership = GroupMembership(
                group=group,
                user=info.context.user,
                status='Pending'
            )
            notification = Notifications(
                    message =f'You have requested to join {group.name}. Wait for admin approval',
                    message_for = info.context.user
                )
            notification.save()
            membership.save()
            return JoinGroup(ok=True, group_membership=membership, message='You have joined this group. Wait for approval')
        if check_membership and check_membership.status == 'Pending':
            return JoinGroup(ok=True, membership=check_membership, message='Status is PendingWait for admin approval')


# this route is used to set the status of the group to Accepted or rejected
class AssertGroupStatus(graphene.Mutation):
    class Arguments:
        membership_id = graphene.Int(required=True)
        status = graphene.String(required=True)

    ok = graphene.Boolean()
    membership = graphene.Field(GroupMembershipType)
    message = graphene.String()

    def mutate(self, info, membership_id, status):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        
        # check status
        if status != 'Accepted' and status != 'Rejected':
            raise GraphQLError('Status can only be set to Accepted or Rejected')
        
        # check membership
        try:
            membership = GroupMembership.objects.get(id=membership_id)
        except GroupMembership.DoesNotExist:
            raise GraphQLError('This membership does not exist')
        

        if membership.group.created_by == info.context.user: # authorized??
        # if status is set to Rejected, that resource is deleted
            if status == 'Rejected': 
                membership.delete()
                return AssertGroupStatus(ok=True, membership=None, message='You have rejected this membership')
        else:
            raise GraphQLError('You are not authorized to accept or reject a group membership request')
        
        # if status is accepted
        membership.status = status
        membership.save()
        notification = Notifications(
                    message = f'{info.context.user.username} accepted your request to join {membership.group.name}',
                    message_for = membership.user
                )
        notification.save()
        return AssertGroupStatus(ok=True, membership=membership, message='You have accepted this membership')
        
class RemoveMemberFromGroup(graphene.Mutation):
    class Arguments:
        membership_id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, membership_id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        
        # check membership
        try:
            membership = GroupMembership.objects.get(id=membership_id)
        except GroupMembership.DoesNotExist:
            raise GraphQLError('This membership does not exist')
        
        if membership.group.created_by == info.context.user: # authorized??
            membership.delete()
            return AssertGroupStatus(ok=True, message='You have removed this membership from the group')
        else:
            raise GraphQLError('You are not authorized to remove someone from the group')
        
class ExitFromGroup(graphene.Mutation):
    class Arguments:
        membership_id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, membership_id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        
        # check membership
        try:
            membership = GroupMembership.objects.get(id=membership_id)
        except GroupMembership.DoesNotExist:
            raise GraphQLError('This membership does not exist')
        
        if membership.user == info.context.user: # authorized??
            membership.delete()
            return AssertGroupStatus(ok=True, message='You have exited from the group')
        else:
            return AssertGroupStatus(ok=False, message='Log in')
            

class DeleteGroup(graphene.Mutation):
    class Arguments:
        group_id = graphene.Int(required=True)
    
    ok = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, group_id):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GraphQLError('Such a group does not exist')
        
        if group.created_by == info.context.user:
            group.delete()
            return DeleteGroup(ok=True, message='You have deleted this group')
        raise GraphQLError('You are not authorised to this')
    
class UpdateGroupDetails(graphene.Mutation):
    class Arguments:
        group_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
    
    ok = graphene.Boolean()
    group = graphene.Field(GroupType)
    message = graphene.String()
    
    def mutate(self, info, group_id, name, description):
        if info.context.user.is_anonymous:
            raise GraphQLError('You are not authenticated. Log in')
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GraphQLError('Such a group does not exist')
        
        if group.created_by == info.context.user:
            group.name = name
            group.description = description
            group.save()
            return UpdateGroupDetails(ok=True, group=group, message='You have updated the details this group')
        raise GraphQLError('You are not authorised to this')
    
class Mutation(graphene.ObjectType):
    create_group = CreateGroup.Field()
    join_group = JoinGroup.Field()
    assert_groupstatus = AssertGroupStatus.Field()
    remove_from_group = RemoveMemberFromGroup.Field()
    exit_group = ExitFromGroup.Field()
    delete_group = DeleteGroup.Field()
    edit_group_details = UpdateGroupDetails.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
