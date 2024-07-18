from django.urls import path
from .views import RegisterView, register_view, login_view,index_view,logout_view,generate_token
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(index_view), name='index'),
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('generate-token/', generate_token, name='generate_token'),


]