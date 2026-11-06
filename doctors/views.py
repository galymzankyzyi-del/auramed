
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from main.models import MedicalService

from .complaints import get_complaints_for_doctor
from .models import Appointment, Doctor


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def appointment_error(request, doctor, message):
    return render(
        request,
        'doctors/appointment_form.html',
        {
            'doctor': doctor,
            'complaint_options': get_complaints_for_doctor(
                doctor.specialization
            ),
            'error': message,
        },
        status=400,
    )


def can_manage_doctor(user, doctor):
    """
    Проверяет право на управление кабинетом врача.
    """
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or doctor.user_id == user.id
        )
    )


def is_past_slot(appointment_date, appointment_time):
    """
    Проверяет, прошло ли выбранное время.
    """
    now = timezone.localtime()

    appointment_datetime = timezone.make_aware(
        datetime.combine(
            appointment_date,
            appointment_time
        ),
        timezone.get_current_timezone()
    )

    return appointment_datetime <= now


def is_valid_slot(doctor, appointment_date, appointment_time):
    """
    Проверяет рабочее время врача и шаг в 30 минут.
    """
    slot_start = datetime.combine(
        appointment_date,
        appointment_time
    )

    slot_end = slot_start + timedelta(minutes=30)

    work_start = datetime.combine(
        appointment_date,
        doctor.work_start
    )

    work_end = datetime.combine(
        appointment_date,
        doctor.work_end
    )

    if slot_start < work_start or slot_end > work_end:
        return False

    minutes_from_start = (
        slot_start - work_start
    ).total_seconds() / 60

    return minutes_from_start % 30 == 0


def get_selected_service(service_id, doctor):
    """
    Получает активную услугу, назначенную врачу.
    Возвращает None, если услуга не выбрана.
    """

    if not service_id:
        return None

    try:
        service_id = int(service_id)
    except (ValueError, TypeError):
        raise ValueError(
            'Некорректный идентификатор услуги.'
        )

    try:
        return MedicalService.objects.get(
            pk=service_id,
            is_active=True,
            doctors=doctor
        )

    except MedicalService.DoesNotExist:
        raise ValueError(
            'Выбранная услуга недоступна у этого врача.'
        )


# ============================================
# 1. СПИСОК ВРАЧЕЙ
# ============================================

def doctor_list(request):

    doctors = Doctor.objects.all()

    return render(
        request,
        'doctors/doctor_list.html',
        {
            'doctors': doctors,
        }
    )


# ============================================
# 2. ДЕТАЛЬНАЯ СТРАНИЦА ВРАЧА
# ============================================

def doctor_detail(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        pk=doctor_id
    )

    return render(
        request,
        'doctors/doctor_detail.html',
        {
            'doctor': doctor,
        }
    )


# ============================================
# 3. РЕДАКТИРОВАНИЕ ПРОФИЛЯ ВРАЧА
# ============================================

@login_required
def edit_profile(request):

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    if request.method == 'POST':

        doctor.name = request.POST.get(
            'name',
            doctor.name
        )

        doctor.specialization = request.POST.get(
            'specialization',
            doctor.specialization
        )

        doctor.experience = request.POST.get(
            'experience',
            doctor.experience
        )

        doctor.phone = request.POST.get(
            'phone',
            doctor.phone
        )

        doctor.description = request.POST.get(
            'description',
            doctor.description
        )

        if 'image' in request.FILES:
            doctor.image = request.FILES['image']

        doctor.save()

        return redirect(
            'doctor_dashboard',
            doctor_id=doctor.id
        )

    return render(
        request,
        'doctors/edit_profile.html',
        {
            'doctor': doctor,
        }
    )


# ============================================
# 4. ОНЛАЙН-ЗАПИСЬ К ВРАЧУ
# ============================================

@login_required(login_url='login')
def book_appointment(request, doctor_id):

    # Записываться могут только пациенты.
    if (
        request.user.is_superuser
        or hasattr(request.user, 'doctor_profile')
    ):
        raise PermissionDenied(
            'Запись доступна только пациентам.'
        )

    doctor = get_object_or_404(
        Doctor,
        pk=doctor_id
    )

    # ----------------------------------------
    # ВЫБРАННАЯ МЕДИЦИНСКАЯ УСЛУГА
    # ----------------------------------------

    # GET: услуга приходит со страницы каталога.
    # POST: услуга приходит из скрытого поля формы.
    if request.method == 'POST':
        service_id = request.POST.get('medical_service')
    else:
        service_id = request.GET.get('service')

    try:
        selected_service = get_selected_service(
            service_id,
            doctor
        )

    except ValueError as error:
        return HttpResponseBadRequest(str(error))

    # Пока календарь поддерживает только 30 минут.
    # Более долгие услуги не разрешаем бронировать,
    # чтобы не создавать пересечения приёмов.
    if (
        selected_service is not None
        and selected_service.duration != 30
    ):
        return HttpResponseBadRequest(
            'Онлайн-запись на эту услугу пока недоступна. '
            'Календарь поддерживает только 30-минутные приёмы.'
        )

    # ----------------------------------------
    # ГОТОВЫЕ ЖАЛОБЫ
    # ----------------------------------------

    complaint_options = get_complaints_for_doctor(
        doctor.specialization
    )

    durations = {
        'today': 'Сегодня',
        '2-3-days': '2–3 дня',
        'week': 'Около недели',
        'month': 'Около месяца',
        'long': 'Более месяца',
    }

    # ----------------------------------------
    # ФОРМА ЗАПИСИ
    # ----------------------------------------

    def render_form(error=None, status=200):

        return render(
            request,
            'doctors/appointment_form.html',
            {
                'doctor': doctor,
                'selected_service': selected_service,
                'complaint_options': complaint_options,
                'error': error,
            },
            status=status
        )

    if request.method != 'POST':
        return render_form()

    # ----------------------------------------
    # ДАННЫЕ ПАЦИЕНТА
    # ----------------------------------------

    patient_name = (
        request.POST.get('patient_name') or ''
    ).strip()

    patient_phone = (
        request.POST.get('patient_phone') or ''
    ).strip()

    date_val = request.POST.get('date')
    time_str = request.POST.get('time')

    selected_complaints = request.POST.getlist(
        'complaints'
    )

    extra_comment = (
        request.POST.get('comment_extra') or ''
    ).strip()

    duration = request.POST.get(
        'symptom_duration',
        ''
    )

    # ----------------------------------------
    # ПРОВЕРКА ДАННЫХ
    # ----------------------------------------

    if not patient_name or not patient_phone:
        return render_form(
            'Укажите имя и номер телефона.',
            400
        )

    if len(patient_name) > 100:
        return render_form(
            'Имя слишком длинное.',
            400
        )

    if len(patient_phone) > 20:
        return render_form(
            'Номер телефона слишком длинный.',
            400
        )

    if len(extra_comment) > 1000:
        return render_form(
            'Комментарий не должен превышать 1000 символов.',
            400
        )

    if len(selected_complaints) > len(complaint_options):
        return render_form(
            'Выбрано слишком много вариантов.',
            400
        )

    if len(selected_complaints) != len(set(selected_complaints)):
        return render_form(
            'Обнаружены повторяющиеся жалобы.',
            400
        )

    if any(
        complaint not in complaint_options
        for complaint in selected_complaints
    ):
        return render_form(
            'Выбран недопустимый вариант жалобы.',
            400
        )

    if duration and duration not in durations:
        return render_form(
            'Некорректная продолжительность симптомов.',
            400
        )

    # ----------------------------------------
    # ФОРМИРОВАНИЕ КОММЕНТАРИЯ
    # ----------------------------------------

    comment_parts = []

    if selected_complaints:
        comment_parts.append(
            'Жалобы: '
            + '; '.join(selected_complaints)
        )

    if duration:
        comment_parts.append(
            'Продолжительность: '
            + durations[duration]
        )

    if extra_comment:
        comment_parts.append(
            'Дополнительно: '
            + extra_comment
        )

    comment = '\n'.join(comment_parts)

    # ----------------------------------------
    # ПРОВЕРКА ДАТЫ И ВРЕМЕНИ
    # ----------------------------------------

    if not date_val or not time_str:
        return render_form(
            'Выберите дату и время приёма.',
            400
        )

    try:
        appointment_date = datetime.strptime(
            date_val,
            '%Y-%m-%d'
        ).date()

        appointment_time = datetime.strptime(
            time_str,
            '%H:%M'
        ).time()

    except (ValueError, TypeError):
        return render_form(
            'Некорректные дата или время.',
            400
        )

    if is_past_slot(
        appointment_date,
        appointment_time
    ):
        return render_form(
            'Нельзя записаться на прошедшее время.',
            400
        )

    if not is_valid_slot(
        doctor,
        appointment_date,
        appointment_time
    ):
        return render_form(
            'Выбранное время вне графика врача.',
            400
        )

    # ----------------------------------------
    # СОХРАНЕНИЕ ЗАПИСИ
    # ----------------------------------------

    with transaction.atomic():

        # Блокируем врача на время бронирования,
        # чтобы два пациента не заняли один слот.
        Doctor.objects.select_for_update().get(
            pk=doctor.pk
        )

        is_booked = Appointment.objects.filter(
            doctor=doctor,
            date=appointment_date,
            time=appointment_time
        ).exclude(
            status='cancelled'
        ).exists()

        if is_booked:
            return render_form(
                'Это время уже занято. Выберите другое.',
                400
            )

        # Повторная проверка активности услуги.
        if selected_service is not None:

            try:
                selected_service = get_selected_service(
                    selected_service.pk,
                    doctor
                )

            except ValueError as error:
                return render_form(
                    str(error),
                    400
                )

            if selected_service.duration != 30:
                return render_form(
                    'Продолжительность услуги изменилась. '
                    'Пожалуйста, обновите страницу.',
                    400
                )

        appointment = Appointment.objects.create(
            patient_user=request.user,
            doctor=doctor,
            patient_name=patient_name,
            patient_phone=patient_phone,
            date=appointment_date,
            time=appointment_time,
            medical_service=selected_service,
            comment=comment,
            status='pending',
        )

    return render(
        request,
        'doctors/appointment_success.html',
        {
            'appointment': appointment,
        }
    )


# ============================================
# 5. ПОЛУЧЕНИЕ СВОБОДНЫХ СЛОТОВ
# ============================================

def get_available_slots(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        pk=doctor_id
    )

    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse(
            {
                'error': 'Дата не указана'
            },
            status=400
        )

    try:
        selected_date = datetime.strptime(
            date_str,
            '%Y-%m-%d'
        ).date()

    except (ValueError, TypeError):
        return JsonResponse(
            {
                'error': 'Некорректная дата'
            },
            status=400
        )

    # Запись на прошедшие даты запрещена.
    if selected_date < timezone.localdate():
        return JsonResponse({
            'slots': []
        })

    # Получаем занятые интервалы.
    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            date=selected_date
        ).exclude(
            status='cancelled'
        ).values_list(
            'time',
            flat=True
        )
    )

    booked_slots = {
        t.strftime('%H:%M')
        for t in booked_times
    }

    slots = []

    current_dt = datetime.combine(
        selected_date,
        doctor.work_start
    )

    end_dt = datetime.combine(
        selected_date,
        doctor.work_end
    )

    # Генерируем интервалы по 30 минут.
    while current_dt + timedelta(minutes=30) <= end_dt:

        slot_time = current_dt.time()
        slot_text = slot_time.strftime('%H:%M')

        in_past = is_past_slot(
            selected_date,
            slot_time
        )

        slots.append({
            'time': slot_text,
            'is_booked': (
                slot_text in booked_slots or in_past
            ),
        })

        current_dt += timedelta(minutes=30)

    return JsonResponse({
        'slots': slots
    })


# ============================================
# 6. ЛИЧНЫЙ КАБИНЕТ ВРАЧА
# ============================================

@login_required
def doctor_dashboard(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        pk=doctor_id
    )

    if not can_manage_doctor(request.user, doctor):
        raise PermissionDenied(
            'Нет доступа к кабинету врача.'
        )

    # ----------------------------------------
    # ВЫБРАННЫЙ РАЗДЕЛ
    # ----------------------------------------

    current_view = request.GET.get(
        'view',
        'pending'
    )

    allowed_views = (
        'pending',
        'completed',
        'cancelled'
    )

    if current_view not in allowed_views:
        current_view = 'pending'

    # ----------------------------------------
    # ФИЛЬТР ПО ДАТЕ
    # ----------------------------------------

    date_filter = request.GET.get(
        'date_filter',
        'all'
    )

    if date_filter not in ('all', 'today', 'date'):
        date_filter = 'all'

    selected_date_str = request.GET.get(
        'date',
        ''
    )

    selected_date = None

    if selected_date_str:
        try:
            selected_date = datetime.strptime(
                selected_date_str,
                '%Y-%m-%d'
            ).date()

        except ValueError:
            selected_date_str = ''

    # ----------------------------------------
    # СОРТИРОВКА
    # ----------------------------------------

    sort_by = request.GET.get(
        'sort',
        'nearest'
    )

    if sort_by not in (
        'nearest',
        'latest',
        'newest'
    ):
        sort_by = 'nearest'

    # ----------------------------------------
    # ЗАПИСИ ТЕКУЩЕГО ВРАЧА
    # ----------------------------------------

    appointments = (
        Appointment.objects
        .filter(
            doctor=doctor,
            status=current_view
        )
        .select_related(
            'patient_user',
            'medical_service'
        )
    )

    if current_view == 'pending':

        if date_filter == 'today':

            appointments = appointments.filter(
                date=timezone.localdate()
            )

        elif date_filter == 'date' and selected_date:

            appointments = appointments.filter(
                date=selected_date
            )

        if sort_by == 'nearest':

            appointments = appointments.order_by(
                'date',
                'time',
                'id'
            )

        elif sort_by == 'latest':

            appointments = appointments.order_by(
                '-date',
                '-time',
                '-id'
            )

        else:

            appointments = appointments.order_by(
                '-id'
            )

    else:

        appointments = appointments.order_by(
            '-date',
            '-time',
            '-id'
        )

    # ----------------------------------------
    # СТАТИСТИКА
    # ----------------------------------------

    counts = {
        'pending': Appointment.objects.filter(
            doctor=doctor,
            status='pending'
        ).count(),

        'completed': Appointment.objects.filter(
            doctor=doctor,
            status='completed'
        ).count(),

        'cancelled': Appointment.objects.filter(
            doctor=doctor,
            status='cancelled'
        ).count(),
    }

    return render(
        request,
        'doctors/doctor_dashboard.html',
        {
            'doctor': doctor,
            'appointments': appointments,
            'current_view': current_view,
            'counts': counts,
            'date_filter': date_filter,
            'selected_date': selected_date_str,
            'sort_by': sort_by,
            'today': timezone.localdate().isoformat(),
        }
    )


# ============================================
# 7. ИЗМЕНЕНИЕ СТАТУСА ПРИЁМА
# ============================================

@login_required
@require_POST
def update_appointment_status(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id
    )

    # Проверяем права врача.
    if not can_manage_doctor(
        request.user,
        appointment.doctor
    ):
        raise PermissionDenied(
            'Нет прав на изменение этой записи.'
        )

    new_status = request.POST.get('status')

    allowed_statuses = {
        'pending',
        'completed',
        'cancelled',
    }

    if new_status not in allowed_statuses:
        return JsonResponse(
            {
                'error': 'Недопустимый статус'
            },
            status=400
        )

    with transaction.atomic():

        doctor = Doctor.objects.select_for_update().get(
            pk=appointment.doctor_id
        )

        appointment.refresh_from_db()

        # Если ранее отменённую запись восстанавливают,
        # убеждаемся, что её время свободно.
        if (
            appointment.status == 'cancelled'
            and new_status != 'cancelled'
        ):

            conflict = Appointment.objects.filter(
                doctor=doctor,
                date=appointment.date,
                time=appointment.time
            ).exclude(
                status='cancelled'
            ).exclude(
                pk=appointment.pk
            ).exists()

            if conflict:
                return JsonResponse(
                    {
                        'error': (
                            'Время уже занято другой записью.'
                        )
                    },
                    status=409
                )

        appointment.status = new_status

        appointment.save(
            update_fields=['status']
        )

    return redirect(
        'doctor_dashboard',
        doctor_id=appointment.doctor_id
    )
