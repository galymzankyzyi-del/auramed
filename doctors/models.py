from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        null=True,
        blank=True,
    )
    name = models.CharField('ФИО', max_length=100)
    specialization = models.CharField('Специализация', max_length=100)
    experience = models.IntegerField('Опыт работы (лет)', default=0)
    phone = models.CharField('Номер телефона', max_length=20)
    description = models.TextField('О себе / Описание', blank=True)
    image = models.ImageField(
        'Фотография врача', upload_to='doctors/', blank=True, null=True
    )

    work_start = models.TimeField('Начало работы', default='09:00')
    work_end = models.TimeField('Конец работы', default='18:00')

    def __str__(self):
        return f'{self.name} ({self.specialization})'


class Appointment(models.Model):
    patient_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_appointments',
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='appointments'
    )
    patient_name = models.CharField('Имя пациента', max_length=100)
    patient_phone = models.CharField('Телефон', max_length=20)
    date = models.DateField('Дата приёма')
    time = models.TimeField('Время приёма')
    comment = models.TextField('Комментарий / Жалобы', blank=True)
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    status = models.CharField(
        'Статус', max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Запись: {self.patient_name} -> {self.doctor.name} ({self.date} {self.time})'