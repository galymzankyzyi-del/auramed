
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from doctors.models import Doctor


# Аккаунт нового врача
class DoctorAccountForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Логин врача'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)

        # Врач не получает права администратора
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

        return user


# Профиль врача: создание и редактирование
class DoctorProfileForm(forms.ModelForm):

    class Meta:
        model = Doctor

        fields = [
            'name',
            'specialization',
            'experience',
            'phone',
            'description',
            'image',
            'work_start',
            'work_end',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'ФИО врача'
            }),
            'specialization': forms.TextInput(attrs={
                'placeholder': 'Например: Кардиолог'
            }),
            'experience': forms.NumberInput(attrs={
                'min': 0,
                'max': 70
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 777 123 45 67'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Информация о враче'
            }),
            'work_start': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'}
            ),
            'work_end': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_experience(self):
        experience = self.cleaned_data['experience']

        if experience < 0 or experience > 70:
            raise forms.ValidationError(
                'Укажите стаж от 0 до 70 лет.'
            )

        return experience

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('work_start')
        end = cleaned_data.get('work_end')

        if start and end and start >= end:
            raise forms.ValidationError(
                'Время окончания работы должно быть позже начала.'
            )

        return cleaned_data


# ========================================
# ФОРМА МЕДИЦИНСКИХ УСЛУГ
# ========================================

from django import forms
from .models import MedicalService


class MedicalServiceForm(forms.ModelForm):

    class Meta:
        model = MedicalService

        fields = [
            'name',
            'category',
            'short_description',
            'description',
            'price',
            'duration',
            'image',
            'doctors',
            'is_active',
            'is_featured',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Название услуги',
            }),

            'short_description': forms.TextInput(attrs={
                'placeholder': 'Кратко опишите услугу',
            }),

            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Что входит в услугу?',
            }),

            'price': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01',
                'placeholder': 'Например: 15000',
            }),

            'duration': forms.NumberInput(attrs={
                'min': '1',
                'placeholder': 'Продолжительность в минутах',
            }),

            'doctors': forms.SelectMultiple(attrs={
                'size': 6,
            }),
        }

        labels = {
            'name': 'Название услуги',
            'category': 'Категория',
            'short_description': 'Краткое описание',
            'description': 'Полное описание',
            'price': 'Стоимость (₸)',
            'duration': 'Продолжительность (мин)',
            'image': 'Фотография',
            'doctors': 'Специалисты',
            'is_active': 'Показывать на сайте',
            'is_featured': 'Популярная услуга',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

        self.fields['image'].widget.attrs['accept'] = (
            'image/jpeg,image/png,image/webp'
        )

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise forms.ValidationError(
                'Стоимость не может быть отрицательной.'
            )

        return price

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')

        if duration is not None and duration < 1:
            raise forms.ValidationError(
                'Продолжительность должна быть больше нуля.'
            )

        return duration

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image and hasattr(image, 'size'):
            if image.size > 3 * 1024 * 1024:
                raise forms.ValidationError(
                    'Изображение не должно превышать 3 МБ.'
                )

        return image
