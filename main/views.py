from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import MedicalService
from .models import PatientProfile
from .patient_forms import PatientUserForm, PatientProfileForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import datetime
from doctors.models import Appointment, Doctor
from .forms import PatientRegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from .admin_forms import DoctorAccountForm, DoctorProfileForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import MedicalService
from .admin_forms import MedicalServiceForm

# ============================================
# 1. ГЛАВНАЯ СТРАНИЦА
# ============================================

def home(request):

    if request.user.is_authenticated:

        # Администратор переходит в свою панель
        if request.user.is_superuser:
            return redirect('admin_dashboard')

        # Врач переходит в свой кабинет
        if hasattr(request.user, 'doctor_profile'):
            return redirect(
                'doctor_dashboard',
                doctor_id=request.user.doctor_profile.id
            )

    # Главная страница для пациентов и гостей
    doctors = Doctor.objects.all()[:4]

    return render(
        request,
        'main/home.html',
        {
            'doctors': doctors,
        }
    )


# ============================================
# 2. ВЫБОР РОЛИ ПРИ РЕГИСТРАЦИИ
# ============================================

def register_role_select(request):
    return render(
        request,
        'main/register_role.html'
    )


# ============================================
# 3. РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
# ============================================

def register_view(request, role):

    # Самостоятельная регистрация доступна
    # только пациентам
    if role != 'patient':
        return redirect('register_role_select')

    # Авторизованному пользователю
    # повторная регистрация не нужна
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':

        form = PatientRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            # Вход после регистрации
            login(request, user)

            return redirect('home')

    else:
        form = PatientRegistrationForm()

    return render(
        request,
        'main/register_form.html',
        {
            'form': form,
            'role': role,
        }
    )


# ============================================
# 4. РЕГИСТРАЦИЯ ПАЦИЕНТА
# ============================================

def register_patient(request):
    return register_view(
        request,
        'patient'
    )


# ============================================
# 5. РЕГИСТРАЦИЯ ВРАЧА
# ============================================

def register_doctor(request):

    # Пока регистрация врача отключена.
    # В дальнейшем добавим подтверждение
    # заявки администратором.
    return redirect('register_role_select')


# ============================================
# 6. ВХОД В СИСТЕМУ
# ============================================


# ============================================
# ВХОД В СИСТЕМУ С ОПРЕДЕЛЕНИЕМ РОЛИ
# ============================================


def login_view(request):

    # Получаем адрес возврата после авторизации
    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or ''
    )

    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Администратор
            if user.is_superuser:
                return redirect('admin_dashboard')

            # Врач
            if hasattr(user, 'doctor_profile'):
                return redirect(
                    'doctor_dashboard',
                    doctor_id=user.doctor_profile.id
                )

            # Пациент: возвращаем на нужную страницу
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)

            return redirect('patient_dashboard')

    else:
        # Уже вошедший пользователь
        if request.user.is_authenticated:
            return redirect('home')

        form = AuthenticationForm()

    return render(
        request,
        'main/login.html',
        {
            'form': form,
            'next': next_url,
        }
    )

# ============================================
# 7. ВЫХОД ИЗ СИСТЕМЫ
# ============================================

def logout_view(request):

    logout(request)

    return redirect('home')


# ============================================
# 8. СТРАНИЦА УСЛУГ
# ============================================


def services_view(request):
    search = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    service_list = (
        MedicalService.objects
        .filter(is_active=True)
        .prefetch_related('doctors')
    )

    if search:
        service_list = service_list.filter(
            Q(name__icontains=search)
            | Q(short_description__icontains=search)
            | Q(description__icontains=search)
        )

    valid_categories = {
        value
        for value, label in MedicalService.CATEGORY_CHOICES
    }

    if category in valid_categories:
        service_list = service_list.filter(
            category=category
        )
    else:
        category = ''

    service_list = service_list.order_by(
        '-is_featured',
        'name'
    )

    return render(
        request,
        'main/services.html',
        {
            'services': service_list,
            'search': search,
            'selected_category': category,
            'categories': MedicalService.CATEGORY_CHOICES,
        }
    )


def service_detail(request, service_id):
    service = get_object_or_404(
        MedicalService.objects.prefetch_related('doctors'),
        pk=service_id,
        is_active=True
    )

    doctors = service.doctors.all()

    return render(
        request,
        'main/service_detail.html',
        {
            'service': service,
            'doctors': doctors,
        }
    )



# ============================================
# 9. ПРОВЕРКА ПРАВ АДМИНИСТРАТОРА
# ============================================

def is_admin(user):

    return (
        user.is_authenticated
        and user.is_active
        and user.is_superuser
    )


# ============================================
# 10. ПАНЕЛЬ АДМИНИСТРАТОРА
# ============================================

@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):

    today = timezone.localdate()

    # ----------------------------------------
    # ОБЩАЯ СТАТИСТИКА
    # ----------------------------------------

    # Количество врачей
    total_doctors = Doctor.objects.count()

    # Количество обычных аккаунтов пациентов
    # без профиля врача
    total_patients = User.objects.filter(
        is_superuser=False,
        is_staff=False,
        doctor_profile__isnull=True
    ).count()

    # Все записи на приём
    total_appointments = Appointment.objects.count()

    # Активные записи
    pending_count = Appointment.objects.filter(
        status='pending'
    ).count()

    # Завершённые записи
    completed_count = Appointment.objects.filter(
        status='completed'
    ).count()

    # Отменённые записи
    cancelled_count = Appointment.objects.filter(
        status='cancelled'
    ).count()

    # Записи на сегодня
    today_count = Appointment.objects.filter(
        date=today
    ).count()

    # ----------------------------------------
    # БЛИЖАЙШИЕ ПРИЁМЫ
    # ----------------------------------------

    upcoming_appointments = (
        Appointment.objects
        .filter(
            status='pending',
            date__gte=today
        )
        .select_related('doctor')
        .order_by(
            'date',
            'time',
            'id'
        )[:8]
    )

    # ----------------------------------------
    # ПОСЛЕДНИЕ СОЗДАННЫЕ ЗАПИСИ
    # ----------------------------------------

    recent_appointments = (
        Appointment.objects
        .select_related('doctor')
        .order_by('-id')[:8]
    )

    # ----------------------------------------
    # ДАННЫЕ ДЛЯ HTML
    # ----------------------------------------

    context = {

        'total_doctors': total_doctors,

        'total_patients': total_patients,

        'total_appointments': total_appointments,

        'pending_count': pending_count,

        'completed_count': completed_count,

        'cancelled_count': cancelled_count,

        'today_count': today_count,

        'upcoming_appointments': upcoming_appointments,

        'recent_appointments': recent_appointments,

        'today': today,
    }

    return render(
        request,
        'main/admin_dashboard.html',
        context
    )



# ============================================
# УПРАВЛЕНИЕ ВРАЧАМИ — АДМИНИСТРАТОР
# ============================================

@login_required
def admin_doctors(request):

    if not request.user.is_superuser:
        raise PermissionDenied

    doctors = (
        Doctor.objects
        .select_related('user')
        .order_by('name')
    )

    return render(
        request,
        'main/admin_doctors.html',
        {
            'doctors': doctors,
        }
    )


# ============================================
# СОЗДАНИЕ НОВОГО ВРАЧА
# ============================================

@login_required
def admin_doctor_create(request):

    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':

        account_form = DoctorAccountForm(
            request.POST,
            prefix='account'
        )

        doctor_form = DoctorProfileForm(
            request.POST,
            request.FILES,
            prefix='doctor'
        )

        account_valid = account_form.is_valid()
        doctor_valid = doctor_form.is_valid()

        if account_valid and doctor_valid:

            with transaction.atomic():

                # Создание аккаунта врача
                user = account_form.save()

                # Создание профиля врача
                doctor = doctor_form.save(commit=False)
                doctor.user = user
                doctor.save()

            return redirect('admin_doctors')

    else:
        account_form = DoctorAccountForm(
            prefix='account'
        )

        doctor_form = DoctorProfileForm(
            prefix='doctor'
        )

    return render(
        request,
        'main/admin_doctor_form.html',
        {
            'account_form': account_form,
            'doctor_form': doctor_form,
            'page_title': 'Добавить врача',
            'is_create': True,
        }
    )


# ============================================
# РЕДАКТИРОВАНИЕ ПРОФИЛЯ ВРАЧА
# ============================================

@login_required
def admin_doctor_edit(request, doctor_id):

    if not request.user.is_superuser:
        raise PermissionDenied

    doctor = get_object_or_404(
        Doctor,
        pk=doctor_id
    )

    if request.method == 'POST':

        doctor_form = DoctorProfileForm(
            request.POST,
            request.FILES,
            instance=doctor,
            prefix='doctor'
        )

        if doctor_form.is_valid():
            doctor_form.save()

            return redirect('admin_doctors')

    else:
        doctor_form = DoctorProfileForm(
            instance=doctor,
            prefix='doctor'
        )

    return render(
        request,
        'main/admin_doctor_form.html',
        {
            'doctor_form': doctor_form,
            'doctor': doctor,
            'page_title': 'Редактировать врача',
            'is_create': False,
        }
    )



# ============================================
# ЛИЧНЫЙ КАБИНЕТ ПАЦИЕНТА
# ============================================

@login_required
def patient_dashboard(request):

    # Администратор использует свою панель
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    # Врач использует свой кабинет
    if hasattr(request.user, 'doctor_profile'):
        return redirect(
            'doctor_dashboard',
            doctor_id=request.user.doctor_profile.id
        )

    today = timezone.localdate()

    # Только записи текущего пользователя
    appointments = (
        Appointment.objects
        .filter(patient_user=request.user)
        .select_related('doctor')
    )

    # Будущие и активные записи
    upcoming_appointments = (
        appointments
        .filter(
            status='pending',
            date__gte=today
        )
        .order_by('date', 'time', 'id')
    )

    # Завершённые
    completed_appointments = (
        appointments
        .filter(status='completed')
        .order_by('-date', '-time', '-id')
    )

    # Отменённые
    cancelled_appointments = (
        appointments
        .filter(status='cancelled')
        .order_by('-date', '-time', '-id')
    )

    # Активные записи, дата которых прошла
    past_pending_appointments = (
        appointments
        .filter(
            status='pending',
            date__lt=today
        )
        .order_by('-date', '-time', '-id')
    )

    context = {
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'past_pending_appointments': past_pending_appointments,

        'upcoming_count': upcoming_appointments.count(),
        'completed_count': completed_appointments.count(),
        'cancelled_count': cancelled_appointments.count(),

        'today': today,
    }

    return render(
        request,
        'main/patient_dashboard.html',
        context
    )


# ============================================
# ОТМЕНА ЗАПИСИ ПАЦИЕНТОМ
# ============================================

@login_required
@require_POST
def patient_cancel_appointment(request, appointment_id):

    # Только пациенты могут использовать этот маршрут
    if (
        request.user.is_superuser
        or hasattr(request.user, 'doctor_profile')
    ):
        raise PermissionDenied

    with transaction.atomic():

        # Блокируем строку записи на время изменения
        appointment = get_object_or_404(
            Appointment.objects.select_for_update(),
            pk=appointment_id,
            patient_user=request.user
        )

        # Отменять разрешено только активную запись
        if appointment.status != 'pending':
            return HttpResponseBadRequest(
                'Эту запись уже нельзя отменить.'
            )

        # Нельзя отменить прошедший приём
        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment.date,
                appointment.time
            ),
            timezone.get_current_timezone()
        )

        if appointment_datetime <= timezone.now():
            return HttpResponseBadRequest(
                'Нельзя отменить прошедший приём.'
            )

        appointment.status = 'cancelled'
        appointment.save(update_fields=['status'])

    return redirect('patient_dashboard')


# ============================================
# ПРОФИЛЬ ПАЦИЕНТА AURAMED
# ============================================

@login_required
def patient_profile(request):

    # Доступ только пациентам
    if (
        request.user.is_superuser
        or hasattr(request.user, 'doctor_profile')
    ):
        raise PermissionDenied(
            'Эта страница доступна только пациентам.'
        )

    # Создаём профиль, если его ещё нет.
    # Это поддерживает старые аккаунты пациентов.
    profile, created = PatientProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        user_form = PatientUserForm(
            request.POST,
            instance=request.user,
            prefix='user'
        )

        profile_form = PatientProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            prefix='profile'
        )

        user_valid = user_form.is_valid()
        profile_valid = profile_form.is_valid()

        if user_valid and profile_valid:

            with transaction.atomic():
                user_form.save()
                profile_form.save()

            return redirect('patient_profile')

    else:
        user_form = PatientUserForm(
            instance=request.user,
            prefix='user'
        )

        profile_form = PatientProfileForm(
            instance=profile,
            prefix='profile'
        )

    return render(
        request,
        'main/patient_profile.html',
        {
            'profile': profile,
            'user_form': user_form,
            'profile_form': profile_form,
        }
    )


# ============================================
# УПРАВЛЕНИЕ МЕДИЦИНСКИМИ УСЛУГАМИ
# ============================================

def require_service_admin(request):
    if not request.user.is_superuser:
        raise PermissionDenied(
            'Доступ разрешён только администратору.'
        )


@login_required(login_url='login')
def admin_services(request):

    require_service_admin(request)

    services = MedicalService.objects.prefetch_related(
        'doctors'
    ).all()

    search = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if search:
        services = services.filter(
            Q(name__icontains=search)
            | Q(short_description__icontains=search)
        )

    valid_categories = {
        choice[0]
        for choice in MedicalService.CATEGORY_CHOICES
    }

    if category in valid_categories:
        services = services.filter(category=category)
    else:
        category = ''

    services = services.order_by('-created_at')

    return render(
        request,
        'main/admin_services.html',
        {
            'services': services,
            'search': search,
            'selected_category': category,
            'categories': MedicalService.CATEGORY_CHOICES,
        }
    )


@login_required(login_url='login')
def admin_service_create(request):

    require_service_admin(request)

    if request.method == 'POST':

        form = MedicalServiceForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            return redirect('admin_services')

    else:
        form = MedicalServiceForm()

    return render(
        request,
        'main/admin_service_form.html',
        {
            'form': form,
            'page_title': 'Добавить услугу',
            'button_text': 'Создать услугу',
            'service': None,
        }
    )


@login_required(login_url='login')
def admin_service_edit(request, service_id):

    require_service_admin(request)

    service = get_object_or_404(
        MedicalService,
        pk=service_id
    )

    if request.method == 'POST':

        form = MedicalServiceForm(
            request.POST,
            request.FILES,
            instance=service
        )

        if form.is_valid():
            form.save()
            return redirect('admin_services')

    else:
        form = MedicalServiceForm(
            instance=service
        )

    return render(
        request,
        'main/admin_service_form.html',
        {
            'form': form,
            'page_title': 'Редактировать услугу',
            'button_text': 'Сохранить изменения',
            'service': service,
        }
    )


@login_required(login_url='login')
@require_POST
def admin_service_toggle(request, service_id):

    require_service_admin(request)

    service = get_object_or_404(
        MedicalService,
        pk=service_id
    )

    service.is_active = not service.is_active
    service.save(update_fields=['is_active', 'updated_at'])

    return redirect('admin_services')
