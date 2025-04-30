from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('link/<str:short_alias>/', views.link_detail, name='link_detail'),
    path('link/<str:short_alias>/delete/', views.delete_link, name='delete_link'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<str:short_alias>/', views.redirect_to_original, name='redirect'),
]