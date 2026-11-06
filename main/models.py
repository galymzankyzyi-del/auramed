
import secrets
from datetime import date

from django.conf import settings
from django.db import models


def generate_patient_demo_id():
    return f"{secrets.randbelow(10**12):012d}"


class PatientProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to='patients/photos/',
        null=True,
        blank=True
    )

    demo_id = models.CharField(
        max_length=12,
        unique=True,
        default=generate_patient_demo_id,
        editable=False
    )

    @property
    def age(self):
        if not self.birth_date:
            return None

        today = date.today()

        return (
            today.year - self.birth_date.year
            - (
                (today.month, today.day)
                < (self.birth_date.month, self.birth_date.day)
            )
        )

    @property
    def clinic_since(self):
        return self.user.date_joined.date()

    def __str__(self):
        return f"{self.user.username} ({self.demo_id})"


# ============================================
# МЕДИЦИНСКИЕ УСЛУГИ AURAMED
# ============================================

from django.db import models


class MedicalService(models.Model):

    CATEGORY_CHOICES = [
        ('consultation', 'Консультации'),
        ('diagnostics', 'Диагностика'),
        ('program', 'Комплексные программы'),
        ('other', 'Другие услуги'),
    ]

    # Название услуги
    name = models.CharField(
        'Название услуги',
        max_length=200
    )

    # Категория
    category = models.CharField(
        'Категория',
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='consultation'
    )

    # Краткое описание для карточки
    short_description = models.CharField(
        'Краткое описание',
        max_length=300,
        blank=True
    )

    # Полное описание услуги
    description = models.TextField(
        'Полное описание',
        blank=True
    )

    # Стоимость в тенге
    price = models.DecimalField(
        'Стоимость (₸)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Продолжительность в минутах
    duration = models.PositiveIntegerField(
        'Продолжительность (минуты)',
        default=30
    )

    # Фото услуги
    image = models.ImageField(
        'Изображение',
        upload_to='services/',
        null=True,
        blank=True
    )

    # Врачи, оказывающие услугу
    doctors = models.ManyToManyField(
        'doctors.Doctor',
        related_name='medical_services',
        blank=True,
        verbose_name='Специалисты'
    )

    # Отображается ли на сайте
    is_active = models.BooleanField(
        'Активна',
        default=True
    )

    # Популярная услуга
    is_featured = models.BooleanField(
        'Популярная услуга',
        default=False
    )

    # Дата создания
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    # Дата изменения
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Медицинская услуга'
        verbose_name_plural = 'Медицинские услуги'
        ordering = ['name']

    def __str__(self):
        return self.name
