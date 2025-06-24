from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken , TokenError


#· · · · · · · · · · · · · · · ·Register Serializer · · · · · · · · · · · · · · · · · · · · · · · ·
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    This serializer handles validation and creation of a new user account.
    It requires `username`, `email`, `password`, and `confirm_password` fields.

    Features:
    - Ensures `password` and `confirm_password` match.
    - Checks for unique `username` and `email`.
    - Uses Django's `create_user()` method to securely hash the password.
    - Excludes `confirm_password` from the created user instance.

    Raises:
        serializers.ValidationError: If passwords do not match or
        if username/email already exist.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email' : {'required' : True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match')

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('Username is already taken! please choose another.')

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('Email is already registered! please login.')

        return data


    def create(self , validated_data):
        validated_data.pop('confirm_password') # added to avoid error 'TypeError: create_user() got an unexpected keyword argument 'confirm_password''
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **validated_data
        )
        return user
#· · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·


#· · · · · · · · · · · · · ·Login Serialzier · · · · · · · · · · · · · · · · · · · · · · · · · ·
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Accepts `username` and `password` fields and is used to authenticate users.

    Features:
    - Ensures both fields are required.
    - Keeps password write-only for security.
    - Used typically with a custom authentication view or token generation.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
#· · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·


#· · · · · · · · · · · · · · · Logout Serializer· · · · · · · · · · · · · · · · · · · · · · · · ·
class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logging out a user by blacklisting their refresh token.

    Requires:
        - `refresh_token` (string): The refresh token to be blacklisted.

    Raises:
        - TokenError: If the token is invalid or already blacklisted.
    """
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        return attrs

    def save(self , **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError as token_error:
            raise serializers.ValidationError({
                'error' : str(token_error),
                'Refresh Token' : 'refresh token is invald or has expired'
            })
#· · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·


#· · · · · · · · · · · · · · · Generates New Access Token· · · · · · · · · · · · · · · · · · · · · · · · ·
class GenerateAccessTokenSerializer(serializers.Serializer):
    """
    Serializer for generating a new access token using a refresh token.

    Validates the given refresh token and prepares the access token
    for generation in the view.

    Fields:
        - refresh_token (str): A valid refresh token issued previously.

    Raises:
        - serializers.ValidationError: If the token is missing or invalid.
    """
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')

        if not refresh_token:
            raise serializers.ValidationError({
                'Refresh Token' : 'Token provided is not a refresh token, Please provide a valid refresh token.'
            })

        try:
            self.refresh = RefreshToken(refresh_token)
        except TokenError:
            raise serializers.ValidationError({
                'Refrsh Token' : 'Refresh token is invalid or has expired , please generate a new refresh token.'
            })
        return attrs
#· · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·