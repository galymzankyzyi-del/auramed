from datetime import date
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

from doctors.models import Appointment, Doctor
# Импортируем формы
from .forms import DoctorRegistrationForm


def home(request):
    # Если пользователь авторизован и он ВРАЧ
    if (
        request.user.is_authenticated
        and hasattr(request.user, 'doctor_profile')
    ):
        doctor = request.user.doctor_profile
        today_date = date.today().strftime('%Y-%m-%d')

        # Записи врача на сегодня
        today_appointments = Appointment.objects.filter(
            doctor=doctor, date=today_date
        )

        total_today = today_appointments.count()
        pending_today = today_appointments.filter(status='pending').count()
        completed_today = today_appointments.filter(
            status='completed'
        ).count()

        # Находим ближайшего ожидающего пациента
        next_appointment = (
            today_appointments.filter(status='pending')
            .order_by('time')
            .first()
        )

        context = {
            'doctor': doctor,
            'today': today_date,
            'total_today': total_today,
            'pending_today': pending_today,
            'completed_today': completed_today,
            'next_appointment': next_appointment,
        }
        return render(request, 'main/home.html', context)

    # Иначе показываем обычный главный экран клиники для пациентов
    return render(request, 'main/home.html')


# Выбор роли при регистрации
def register_role_select(request):
    return render(request, 'main/register_role.html')


# Регистрация
def register_view(request, role):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            if role == 'doctor':
                user.is_staff = True
                user.save()
                # Автоматически создаем пустой профиль Doctor, чтобы связать с user
                Doctor.objects.get_or_create(user=user)

            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(
        request, 'main/register_form.html', {'form': form, 'role': role}
    )


# Вход
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Если это врач — перенаправляем в кабинет
            if hasattr(user, 'doctor_profile'):
                return redirect(
                    'doctor_dashboard', doctor_id=user.doctor_profile.id
                )
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})


# Выход
def logout_view(request):
    logout(request)
    return redirect('home')