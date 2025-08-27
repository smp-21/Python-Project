from django.urls import path
from . import views

app_name = 'stock_analysis'

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_stocks, name='analyze_stocks'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
] 