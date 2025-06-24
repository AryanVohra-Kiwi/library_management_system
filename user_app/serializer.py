from rest_framework import serializers
from books.models import IssueBook
from .models import CustomerCreate

#· · ────── ꒰ঌ· Customer Serializer·໒꒱ ────── · ·
class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerCreate model.
    Exposes profile fields along with the user's username and email (read-only).
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = CustomerCreate
        exclude = ('user',)
#· · ────── ꒰ঌ·✦·໒꒱ ────── · ·

#· · ────── ꒰ঌ· Update Customer Serializer·໒꒱ ────── · ·
class CustomerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used to update customer profile fields.
    Only editable profile-related fields are exposed.
    """
    profile_picture = serializers.ImageField(required=False)
    email = serializers.CharField(source='user.email', required=False)
    class Meta:
        model = CustomerCreate
        fields = ['first_name', 'last_name', 'age', 'phone', 'email', 'profile_picture']

    def validate_age(self, data):
        if data is not None and (data < 0 or data > 100):
            raise serializers.ValidationError('Please enter a valid age')
        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
#· · ────── ꒰ঌ·✦·໒꒱ ────── · ·

#· · ────── ꒰ঌ· Change Customer password Serializer·໒꒱ ────── · ·
class PasswordChnageSerializer(serializers.Serializer):
    """
    Serializer for handling password change requests.

    Validates that the new password and its confirmation match.
    Old password will be verified separately in the view.
    """
    old_password = serializers.CharField(
        required=True ,
        write_only=True ,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True ,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True ,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        new_pass = attrs.get('new_password')
        confirm_pass = attrs.get('confirm_password')

        if new_pass != confirm_pass:
            raise serializers.ValidationError('Passwords do not match')
        return attrs
#· · ────── ꒰ঌ·✦·໒꒱ ────── · ·

#· · ────── ꒰ঌ· IssueBook  Serializer·໒꒱ ────── · ·
class IssueBookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='book.book_instance.Title', read_only=True)
    book_structure_id = serializers.IntegerField(source='book.book_instance.id', read_only=True)
    class Meta:
        model = IssueBook
        fields = ['title', 'book_structure_id', 'issue_date', 'return_date']
#· · ────── ꒰ঌ·✦·໒꒱ ────── · ·