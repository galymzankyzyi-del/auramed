
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PatientRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )

    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вашу фамилию'
        })
    )

    email = forms.EmailField(
        label='Электронная почта',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@gmail.com'
        })
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Логин'
        self.fields['username'].help_text = (
            'До 150 символов. Буквы, цифры и символы @/./+/-/_.'
        )

        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = (
            'Не менее 8 символов. '
            'Не используйте слишком простой пароль.'
        )

        self.fields['password2'].label = 'Повторите пароль'
        self.fields['password2'].help_text = (
            'Введите пароль ещё раз для подтверждения.'
        )

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].widget.attrs[
            'placeholder'
        ] = 'Придумайте логин'

        self.fields['password1'].widget.attrs[
            'placeholder'
        ] = 'Придумайте пароль'

        self.fields['password2'].widget.attrs[
            'placeholder'
        ] = 'Повторите пароль'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Пользователь с такой почтой уже зарегистрирован.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
