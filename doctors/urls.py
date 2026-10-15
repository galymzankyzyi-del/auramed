from django.urls import path
from . import views

urlpatterns = [
    # Список всех врачей
    path('', views.doctor_list, name='doctor_list'),
    
    # Редактирование профиля врача (обязательно ВЫШЕ путей с <int:doctor_id>)
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Личный кабинет врача
    path('<int:doctor_id>/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Детали конкретного врача
    path('<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    
    # Запись на приём и слоты
    path('<int:doctor_id>/book/', views.book_appointment, name='book_appointment'),
    path('<int:doctor_id>/slots/', views.get_available_slots, name='get_available_slots'),
    
    # Изменение статуса приёма
    path('appointment/<int:appointment_id>/status/', views.update_appointment_status, name='update_appointment_status'),
    
]