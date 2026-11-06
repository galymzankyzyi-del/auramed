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
    path(
    'dashboard/admin/',
    views.admin_dashboard,
    name='admin_dashboard'
),
    path(
    'dashboard/admin/doctors/',
    views.admin_doctors,
    name='admin_doctors'
),

    path(
        'dashboard/admin/doctors/create/',
        views.admin_doctor_create,
        name='admin_doctor_create'
    ),

    path(
        'dashboard/admin/doctors/<int:doctor_id>/edit/',
        views.admin_doctor_edit,
        name='admin_doctor_edit'
    ),

    path(
    'patient/dashboard/',
    views.patient_dashboard,
    name='patient_dashboard'
),

    path(
        'patient/appointments/<int:appointment_id>/cancel/',
        views.patient_cancel_appointment,
        name='patient_cancel_appointment'
    ),

    path(
        'patient/profile/',
        views.patient_profile,
        name='patient_profile'
    ),

    path(
        'dashboard/admin/services/',
        views.admin_services,
        name='admin_services'
    ),

    path(
        'dashboard/admin/services/create/',
        views.admin_service_create,
        name='admin_service_create'
    ),

    path(
        'dashboard/admin/services/<int:service_id>/edit/',
        views.admin_service_edit,
        name='admin_service_edit'
    ),

    path(
        'dashboard/admin/services/<int:service_id>/toggle/',
        views.admin_service_toggle,
        name='admin_service_toggle'
    ),
    path(
        'services/<int:service_id>/',
        views.service_detail,
        name='service_detail'
    ),
]