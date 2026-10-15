from django import forms
from .models import Doctor


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
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-input', 'placeholder': 'Иванов Иван Иванович'}
            ),
            'specialization': forms.TextInput(
                attrs={'class': 'form-input', 'placeholder': 'Терапевт'}
            ),
            'experience': forms.NumberInput(
                attrs={'class': 'form-input', 'placeholder': '5'}
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': '+7 700 000 00 00',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-input',
                    'rows': 3,
                    'placeholder': 'Обо мне...',
                }
            ),
            'image': forms.FileInput(attrs={'class': 'form-file'}),
        }

        