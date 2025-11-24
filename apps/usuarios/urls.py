from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('login/', 
        auth_views.LoginView.as_view(
            template_name='home/login.html',
            redirect_authenticated_user=True,
            next_page='usuarios:dashboard'
        ), 
        name='login'
    ),
    path('logout/', views.custom_logout, name='logout'),

    # Gestión de usuarios (solo administradores)
    path('', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar'),
    path('perfil/<int:pk>/', views.perfil_usuario, name='perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]