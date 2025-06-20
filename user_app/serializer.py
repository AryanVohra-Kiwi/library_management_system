from rest_framework import serializers
from .models import CustomerCreate
from django.contrib.auth.forms import PasswordChangeForm

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCreate
        fields = '__all__'


class CustomerUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    class Meta:
        model = CustomerCreate
        fields = ['first_name', 'last_name', 'age', 'phone', 'email', 'profile_picture']

class PasswordChnageSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Passwords do not match')
        return attrs


