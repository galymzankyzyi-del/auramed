from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Appointment, Doctor


# Проверка: является ли пользователь админом
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# 1. Список врачей
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(
        request, 'doctors/doctor_list.html', {'doctors': doctors}
    )


# 2. Детальная страница врача
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(
        request, 'doctors/doctor_detail.html', {'doctor': doctor}
    )


# 3. Редактирование профиля (только для админа)
@user_passes_test(is_admin)
def edit_profile(request):
    # Если редактируем профиль авторизованного врача
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        doctor.name = request.POST.get('name')
        doctor.specialization = request.POST.get('specialization')
        doctor.experience = request.POST.get('experience')
        doctor.phone = request.POST.get('phone')
        doctor.save()
        return redirect('doctor_detail', doctor_id=doctor.id)

    return render(
        request, 'doctors/edit_doctor_profile.html', {'doctor': doctor}
    )


# 4. Онлайн-запись на приём
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        patient_phone = request.POST.get('patient_phone')
        date_val = request.POST.get('date')
        time_val = request.POST.get('time')
        comment = request.POST.get('comment', '')

        # Защита от дублирования записи на одно время
        if Appointment.objects.filter(
            doctor=doctor, date=date_val, time=time_val
        ).exists():
            return render(
                request,
                'doctors/appointment_form.html',
                {
                    'doctor': doctor,
                    'error': 'К сожалению, это время уже занято. Выберите другое.',
                },
            )

        appointment = Appointment.objects.create(
            doctor=doctor,
            patient_name=patient_name,
            patient_phone=patient_phone,
            date=date_val,
            time=time_val,
            comment=comment,
        )

        return render(
            request,
            'doctors/appointment_success.html',
            {'appointment': appointment},
        )

    return render(
        request, 'doctors/appointment_form.html', {'doctor': doctor}
    )


# 5. AJAX-слоты времени для календаря
def get_available_slots(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Дата не указана'}, status=400)

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor, date=date_str
        ).values_list('time', flat=True)
    )
    booked_slots = {t.strftime('%H:%M') for t in booked_times}

    slots = []
    current_dt = datetime.combine(datetime.today(), doctor.work_start)
    end_dt = datetime.combine(datetime.today(), doctor.work_end)

    while current_dt < end_dt:
        slot_time = current_dt.strftime('%H:%M')
        slots.append(
            {
                'time': slot_time,
                'is_booked': slot_time in booked_slots,
            }
        )
        current_dt += timedelta(minutes=30)

    return JsonResponse({'slots': slots})


# 6. Журнал записей / Рабочий кабинет врача
def doctor_dashboard(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = selected_date_str
    else:
        selected_date = date.today().strftime('%Y-%m-%d')

    appointments = Appointment.objects.filter(
        doctor=doctor, date=selected_date
    )

    return render(
        request,
        'doctors/doctor_dashboard.html',
        {
            'doctor': doctor,
            'appointments': appointments,
            'selected_date': selected_date,
            'today': date.today().strftime('%Y-%m-%d'),
        },
    )


# 7. Изменение статуса приёма (Ожидает / Принят / Отмена)
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'completed', 'cancelled']:
            appointment.status = new_status
            appointment.save()

    return redirect('doctor_dashboard', doctor_id=appointment.doctor.id)