from django.contrib import admin

from .models import Appointment, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience', 'phone', 'user')
    search_fields = ('name', 'specialization', 'phone')
    list_filter = ('specialization',)

    # Только суперадмин/персонал с правами может менять карточки
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name',
        'doctor',
        'date',
        'time',
        'patient_phone',
        'created_at',
    )
    list_filter = ('doctor', 'date')
    search_fields = ('patient_name', 'patient_phone')

    