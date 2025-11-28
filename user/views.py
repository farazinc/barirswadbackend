from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    if User.objects.filter(username=data['email']).exists():
        return Response({"error": "Email already registered"}, status=400)

    user = User.objects.create(
        username=data['email'],
        email=data['email'],
        password=make_password(data['password'])
    )

    UserProfile.objects.create(
        uid=user,
        name=data['name'],
        profilePic=None,
        role=data.get('role', 'user')  # default to 'user'
    )

    return Response({"message": f"{data.get('role', 'user').capitalize()} registered"}, status=201)



@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    user = authenticate(username=data['email'], password=data['password'])
    if user is None:
        return Response({"error": "Invalid credentials"}, status=401)

    return Response({
        "uid": user.id,
        "name": user.profile.name,
        "email": user.email,
        "profilePic": user.profile.profilePic,
        "role": user.profile.role,
        "createdAt": str(user.profile.createdAt)
    })


@api_view(['GET'])
def profile(request, uid):
    try:
        user = User.objects.get(id=uid)
        ser = UserSerializer(user)
        return Response(ser.data)
    except:
        return Response({"error": "User not found"}, status=404)
