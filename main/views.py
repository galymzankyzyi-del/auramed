from datetime import date
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from doctors.models import Appointment, Doctor
from .forms import DoctorRegistrationForm


# Главная страница (если зашел врач — перенаправляем в его кабинет из приложения doctors)
def home(request):
    if request.user.is_authenticated and hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard', doctor_id=request.user.doctor_profile.id)

    # Для обычных пациентов и гостей — витрина клиники
    doctors = Doctor.objects.all()[:4]
    context = {
        'doctors': doctors,
    }
    return render(request, 'main/home.html', context)


# Выбор роли при регистрации
def register_role_select(request):
    return render(request, 'main/register_role.html')


# Регистрация (универсальная)
def register_view(request, role):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            if role == 'doctor':
                user.is_staff = True
                user.save()
                # Автоматически создаем пустой профиль Doctor
                Doctor.objects.get_or_create(user=user)

            login(request, user)
            
            # Если зарегистрировался врач — сразу в его дашборд
            if hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard', doctor_id=user.doctor_profile.id)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(
        request, 'main/register_form.html', {'form': form, 'role': role}
    )


# Отдельные вспомогательные вьюхи регистрации (если вызываются из urls)
def register_patient(request):
    return register_view(request, 'patient')


def register_doctor(request):
    return register_view(request, 'doctor')


# Вход в систему
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Если это врач — перенаправляем в его личный кабинет
            if hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard', doctor_id=user.doctor_profile.id)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})


# Выход из системы
def logout_view(request):
    logout(request)
    return redirect('home')


# Страница услуг
def services_view(request):
    return render(request, 'main/services.html')