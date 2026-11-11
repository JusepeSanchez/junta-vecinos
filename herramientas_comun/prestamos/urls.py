from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('herramientas/', views.herramienta_list, name='herramienta_list'),
    path('herramientas/nueva/', views.herramienta_create, name='herramienta_create'),
    path('herramientas/<int:pk>/', views.herramienta_detail, name='herramienta_detail'),
    path('herramientas/<int:pk>/editar/', views.herramienta_edit, name='herramienta_edit'),
    path('herramientas/<int:pk>/eliminar/', views.herramienta_delete, name='herramienta_delete'),
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_edit, name='categoria_edit'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('solicitud/', views.ver_solicitud, name='ver_solicitud'),
    path('solicitud/agregar/<int:pk>/', views.agregar_solicitud, name='agregar_solicitud'),
    path('solicitud/quitar/<int:pk>/', views.quitar_solicitud, name='quitar_solicitud'),
    path('solicitud/confirmar/', views.confirmar_solicitud, name='confirmar_solicitud'),
    path('mis-prestamos/', views.mis_prestamos, name='mis_prestamos'),
    path('mis-prestamos/<int:pk>/cancelar/', views.cancelar_prestamo, name='cancelar_prestamo'),
    path('prestamos/', views.todos_prestamos, name='todos_prestamos'),
    path('prestamos/<int:pk>/activar/', views.activar_prestamo, name='activar_prestamo'),
    path('prestamos/<int:pk>/devolucion/', views.registrar_devolucion, name='registrar_devolucion'),
]
