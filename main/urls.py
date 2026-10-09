from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'register/select/',
        views.register_role_select,
        name='register_role_select',
    ),
    path(
        'register/<str:role>/', views.register_view, name='register_by_role'
    ),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]