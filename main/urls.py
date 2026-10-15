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
    path('services/', views.services_view, name='services'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),

]