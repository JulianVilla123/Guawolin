from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from tickets import views
from django.conf import settings
from django.conf.urls.static import static
from tickets.views import CustomLoginView
from tickets.views import profile_settings

urlpatterns = [
    path('', views.home, name='home'), # ✅ Esto conecta la raíz con la vista 'home'
    path('home/', views.home, name='home'),  # Esto hace que la raíz muestre tu pantalla principal
    path('admin/', admin.site.urls),
    path('eventos/', views.eventos_disponibles, name='eventos_disponibles'),  # Vista para asistentes
    path('tickets/', include('tickets.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),   
    path('profile/', profile_settings, name='profile_settings'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path("como-usar/", views.como_usar_fiestapp, name="como_usar"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)