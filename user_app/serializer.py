from rest_framework import serializers

from books.models import IssueBook
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

class IssueBookSerializer(serializers.ModelSerializer):
    Title = serializers.CharField(source='book.book_instance.Title', read_only=True)
    book_copy_id = serializers.IntegerField(source='book.book_instance.id', read_only=True)
    class Meta:
        model = IssueBook
        fields = ['Title', 'book_copy_id', 'Issue_date', 'Return_date']
