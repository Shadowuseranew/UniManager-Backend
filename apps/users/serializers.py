from rest_framework import serializers

from apps.users.models import User, UserRole
from apps.users.services import create_user_account


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        attrs.pop('password_confirm')
        return attrs

    def create(self, validated_data: dict) -> User:
        return create_user_account(**validated_data)
