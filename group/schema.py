import graphene
from graphene_django import DjangoObjectType
from .models import Group, GroupMembership

class GroupType(DjangoObjectType):
    membership_count = graphene.Int()

    def resolve_membership_count(self, info):
        return self.membership_count()
    
    class Meta:
        model = Group
        fields = ("id", "name", "created_at", "updated_at", "created_by")


class GroupMembershipType(DjangoObjectType):
    class Meta:
        model = GroupMembership
        fields = ("id", "group", "status", "created_at", "updated_at")