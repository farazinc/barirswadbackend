from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('user', 'User'), ('seller', 'Seller')], default='user')



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    profilePic = serializers.CharField(source='profile.profilePic')
    role = serializers.CharField(source='profile.role')
    createdAt = serializers.DateTimeField(source='profile.createdAt')

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profilePic', 'role', 'createdAt']
