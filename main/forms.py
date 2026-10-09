from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PatientRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

class DoctorRegistrationForm(forms.ModelForm): # Make sure the class name matches exactly
    class Meta:
        # your form configuration
        pass