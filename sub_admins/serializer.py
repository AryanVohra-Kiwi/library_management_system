from django.contrib.auth.models import Group, User, Permission
from django.contrib.auth import get_backends
from rest_framework import serializers
from .models import SubAdmin

class SubAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    last_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    permissions = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    # Read-only field to show assigned permissions
    assigned_permissions = serializers.SerializerMethodField(read_only=True)

    def get_assigned_permissions(self, obj):
        if not hasattr(obj, 'user') or not obj.user:
            return []
        return list(obj.user.user_permissions.values_list('codename', flat=True))

    class Meta:
        model = SubAdmin
        exclude = ('user',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'user') and instance.user:
            data['username'] = instance.user.username
            data['first_name'] = instance.user.first_name
            data['last_name'] = instance.user.last_name
            data['email'] = instance.user.email
        return data

    def create(self, validated_data):
        # Extract user-related fields from top level
        username = validated_data.pop('username')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        permissions = validated_data.pop('permissions', [])  # Fixed typo

        # Check if username exists
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        try:
            group = Group.objects.get(name='sub-admin')
            group.user_set.add(user)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group 'sub-admin' does not exist.")

        subadmin = SubAdmin.objects.create(user=user, **validated_data)

        # Handle permissions - set on user, not subadmin
        allowed_codenames = {'ReadBook', 'UpdateBook', 'DeleteBook'}
        requested_perms = set(permissions)
        valid_codenames = allowed_codenames.intersection(requested_perms)
        perms = Permission.objects.filter(codename__in=valid_codenames)
        user.user_permissions.set(perms)  # Fixed: set on user, not subadmin

        return subadmin

    def update(self, instance, validated_data):
        # Extract user-related fields
        username = validated_data.pop('username', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        permissions = validated_data.pop('permissions', None)

        user = instance.user

        # Update user fields
        if username is not None:
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if password is not None:
            user.set_password(password)

        user.save()

        if permissions is not None:
            allowed_codenames = {'ReadBook', 'UpdateBook', 'DeleteBook'}
            valid_codenames = set(permissions).intersection(allowed_codenames)
            perms = Permission.objects.filter(codename__in=valid_codenames)
            user.user_permissions.set(perms)

        # Update SubAdmin model fields if any remaining
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance