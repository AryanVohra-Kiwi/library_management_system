from django.contrib.auth.models import Group, User, Permission
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
    assigned_permissions = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = SubAdmin
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_assigned_permissions(self, obj):
        if hasattr(obj, 'user') and obj.user:
            # Get all permissions (direct + group permissions)
            all_permissions = obj.user.get_all_permissions()
            return list(all_permissions)

        # If SubAdmin itself is the user (inherits from User)
        elif hasattr(obj, 'get_all_permissions'):
            return list(obj.get_all_permissions())
        return []

    def create(self, validated_data):
        username = validated_data.pop('username')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        permissions = validated_data.pop('permission' , [])

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