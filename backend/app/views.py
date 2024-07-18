from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from .models import Author, Song, Like
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


API_KEY = "aaabbbccc"  




@login_required
def index_view(request):
    token = None
    data = None
    show_keys = False

    if request.method == 'POST':
        if 'generate_keys' in request.POST:
            refresh = RefreshToken.for_user(request.user)
            token = refresh.access_token
            show_keys = True
        else:
            submitted_key = request.POST.get('key')
            try:
                # Verify the submitted JWT token
                access_token = AccessToken(submitted_key)
                if access_token['user_id'] == request.user.id:
                    data = {
                        'authors': Author.objects.all(),
                        'songs': Song.objects.all(),
                        'likes': Like.objects.all(),
                    }
                else:
                    messages.warning(request, 'Invalid token or access denied. Please try again.')
            except Exception:
                # Handle invalid token
                if submitted_key == API_KEY:
                    data = {
                        'authors': Author.objects.all(),
                        'songs': Song.objects.all(),
                        'likes': Like.objects.all(),
                    }
                else:
                    messages.warning(request, 'Invalid token or access denied. Please try again.')

    context = {
        'token': str(token) if token else None,
        'api_key': API_KEY,
        'show_keys': show_keys,
        'data': data,
    }
    return render(request, 'index.html', context)

@login_required
def generate_token(request):
    refresh = RefreshToken.for_user(request.user)
    return redirect('index')

@api_view(['POST'])
def create_auth_token(request):
    if request.method == 'POST':
        user = request.user
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

 

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

def register_view(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        else:
            for error in serializer.errors.values():
                messages.error(request, error[0])
    return render(request, 'register.html')
