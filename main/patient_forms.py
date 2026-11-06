
from datetime import date

from django import forms
from django.contrib.auth import get_user_model

from .models import PatientProfile


User = get_user_model()


class PatientUserForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'email',
        ]

        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Ваша фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'example@gmail.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if email and User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                'Эта почта уже используется другим пользователем.'
            )

        return email


class PatientProfileForm(forms.ModelForm):

    class Meta:
        model = PatientProfile

        fields = [
            'phone',
            'birth_date',
            'image',
        ]

        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 777 123 45 67'
            }),
            'birth_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['birth_date'].input_formats = [
            '%Y-%m-%d'
        ]

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['image'].widget.attrs['accept'] = (
            'image/jpeg,image/png,image/webp'
        )

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date and birth_date > date.today():
            raise forms.ValidationError(
                'Дата рождения не может быть в будущем.'
            )

        return birth_date

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image and hasattr(image, 'size'):
            if image.size > 3 * 1024 * 1024:
                raise forms.ValidationError(
                    'Размер фотографии не должен превышать 3 МБ.'
                )

        return image
