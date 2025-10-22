from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from tickets import views


urlpatterns = [
    path('', views.home, name='home'), # ✅ Esto conecta la raíz con la vista 'home'
    path('home/', views.home, name='home'),  # Esto hace que la raíz muestre tu pantalla principal
    path('admin/', admin.site.urls),
    path('eventos/', views.events, name='events'),
    path('tickets/', include('tickets.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='guawolin/login.html'), name='login'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
