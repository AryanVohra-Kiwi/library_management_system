from django.contrib.auth.models import Group, User, Permission
from django.contrib.auth import get_backends
from rest_framework import serializers
from .models import SubAdmin
class SubAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    permissions = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    # Read-only field to show assigned permissions
    assigned_permissions = serializers.SerializerMethodField(read_only=True) #uses get_assigned_permission functions return value
    #bug here fix later
    def get_assigned_permissions(self, obj):
        if not hasattr(obj, 'user') or not obj.user:
            print("no attr")
            return []
        user = obj.user
        all_permissions = set()
        for perm in user.user_permissions.all():
            all_permissions.add(perm.codename)
        return (list(all_permissions))

    class Meta:
        model = SubAdmin
        exclude = ('user',)
        extra_kwargs = {
            'password': {'write_only': True},
        }



    def create(self, validated_data):
        user_data = validated_data.pop('user')
        username = user_data.get('username')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        email = user_data.get('email')
        password = user_data.get('password')
        permissions = user_data.get('permission' , [])

        #check if username exists
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists')

        user = User.objects.create_user(
            username=username,
            first_name=first_name ,
            last_name=last_name,
            email=email,
            password=password
        )
        user.save()

        try:
            group = Group.objects.get(name='sub-admin')
            group.user_set.add(user)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group 'admin' does not exist.")

        subadmin = SubAdmin.objects.create(user=user)

        allowed_codenames = {'ReadBook' , 'UpdateBook' , 'DeleteBook'}
        requested_perms = set(permissions)
        valid_codename = allowed_codenames.intersection(requested_perms)
        perms = Permission.objects.filter(codename__in=valid_codename)
        subadmin.permissions.set(perms)

        return subadmin