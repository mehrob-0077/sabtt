from datetime import date, datetime, time, timedelta
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import AppointmentForm, ServiceForm
from .models import Appointment, Category, Service
from .permissions import custom_login_required, custom_staff_required


def home_view(request):
    categories = Category.objects.annotate(service_count=Count('services', filter=Q(services__is_active=True))).order_by('name')
    return render(request, 'work/home.html', {'categories': categories})


def service_list_view(request):
    services = Service.objects.select_related('category')
    if not request.user.is_staff:
        services = services.filter(is_active=True)

    search = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    city = request.GET.get('city', '')

    if search:
        services = services.filter(Q(name__icontains=search) | Q(description__icontains=search))

    if category_id.isdigit():
        services = services.filter(category_id=category_id)

    if city:
        services = services.filter(city__icontains=city)

    return render(request, 'work/service_list_view.html', {'services': services,'categories': Category.objects.all().order_by('name'),'search': search,'selected_category': category_id,'selected_city': city,})


def category_detail_view(request, id):
    category = get_object_or_404(Category, pk=id)
    services = Service.objects.filter(category=category).select_related('category')
    if not request.user.is_staff:
        services = services.filter(is_active=True)
    return render(request, 'work/service_list_view.html', {'services': services,'categories': Category.objects.all().order_by('name'),'search': '','selected_category': str(category.id),'selected_city': '','current_category': category,})


def service_detail_view(request, id):
    services = Service.objects.select_related('category')
    if not request.user.is_staff:
        services = services.filter(is_active=True)
        
    service = get_object_or_404(services, pk=id)
    return render(request, 'work/service_detail.html', {'service': service})


@custom_staff_required
def create_service_view(request):
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.owner = request.user
            service.save()
            return redirect('service_list_view')
        return render(request, 'work/create_service_view.html', {
            'error': 'Пожалуйста, проверьте заполненные данные.',
            'categories': categories,
            'service': form.instance,
        })
    return render(request, 'work/create_service_view.html', {'categories': categories})


@custom_staff_required
def update_service_view(request, id):
    service = get_object_or_404(Service, pk=id)
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            service = form.save()
            return redirect('service_detail_view', id=service.id)
        return render(request, 'work/update_service_view.html', {
            'service': form.instance,
            'categories': categories,
            'error': 'Пожалуйста, проверьте заполненные данные.',
        })
    return render(request, 'work/update_service_view.html', {'service': service, 'categories': categories})


@custom_staff_required
def delete_service_view(request, id):
    service = get_object_or_404(Service, pk=id)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list_view')
    return render(request, 'work/delete_service_view.html', {'service': service})


@custom_staff_required
def view_trash(request):
    services = Service.all_objects.filter(is_deleted=True).order_by('-deleted_at')
    return render(request, 'work/trash.html', {'services': services})


@custom_staff_required
def restore_product(request, id):
    if request.method == 'POST':
        service = get_object_or_404(Service.all_objects, id=id, is_deleted=True)
        service.restore()
    return redirect('service_list_view')


@custom_staff_required
def hard_delete_product_view(request, id):
    if request.method == 'POST':
        service = get_object_or_404(Service.all_objects, id=id, is_deleted=True)
        service.hard_delete()
    return redirect('view_trash')


@custom_staff_required
def category_list_view(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'work/category_list.html', {'categories': categories})


@custom_staff_required
def create_category_view(request):
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '')
        image = request.FILES.get('image')
        if not name:
            error = 'Введите название категории.'
        elif not image:
            error = 'Загрузите фото категории.'

        elif Category.objects.filter(name__iexact=name).exists():
            error = 'Такая категория уже существует.'
        else:
            Category.objects.create(name=name, image=image)
            return redirect('category_list_view')
    return render(request, 'work/category_form.html', {'name': request.POST.get('name', ''), 'error': error, 'page_title': 'Новая категория'})


@custom_staff_required
def update_category_view(request, id):
    category = get_object_or_404(Category, pk=id)
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '')
        image = request.FILES.get('image')
        if not name:
            error = 'Введите название категории.'
        elif Category.objects.filter(name__iexact=name).exclude(pk=category.pk).exists():
            error = 'Такая категория уже существует.'
        else:
            category.name = name
            update_fields = ['name']
            if image:
                category.image = image
                update_fields.append('image')
            category.save(update_fields=update_fields)
            return redirect('category_list_view')
    return render(request, 'work/category_form.html', {'category': category, 'name': category.name, 'error': error, 'page_title': 'Изменить категорию'})


@custom_staff_required
def delete_category_view(request, id):
    category = get_object_or_404(Category, pk=id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list_view')
    return render(request, 'work/category_delete.html', {'category': category})


@custom_login_required
def appointment_create_view(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    form = AppointmentForm(request.POST or None)
    selected_date = request.POST.get('date') or request.GET.get('date', '')
    available_times = []

    if request.user.is_staff or service.owner_id == request.user.pk:
        return render(request, 'work/appointment_create.html', {
            'service': service,
            'error': 'Нельзя записаться на собственную услугу.',
            'today': timezone.localdate().isoformat(),
            'is_service_owner': True,
        })

    if request.method == 'POST' and form.is_valid():
        appointment_date = form.cleaned_data['date']
        appointment_time = form.cleaned_data['time']

        if appointment_time in available_appointment_times(service, appointment_date):
            Appointment.objects.create(
                user=request.user,
                service=service,
                date=appointment_date,
                time=appointment_time,
                note=form.cleaned_data['note'],
            )
            return redirect('my_appointments_view')

    if selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
            available_times = available_appointment_times(service, selected_date)
            selected_date = selected_date.isoformat()
        except ValueError:
            selected_date = ''

    return render(request, 'work/appointment_create.html', {
        'service': service,
        'error': 'Выбранная дата или время недоступны.' if request.method == 'POST' else None,
        'today': timezone.localdate().isoformat(),
        'selected_date': selected_date,
        'available_times': available_times,
        'note': request.POST.get('note', ''),
    })


def appointment_time_is_available(service, appointment_date, appointment_time, exclude_appointment_id=None):
    existing_appointments = Appointment.objects.filter(
        service=service,
        date=appointment_date,
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_ACCEPTED],
    )

    if exclude_appointment_id:
        existing_appointments = existing_appointments.exclude(pk=exclude_appointment_id)

    for existing_appointment in existing_appointments:
        requested_start = datetime.combine(appointment_date, appointment_time)
        existing_start = datetime.combine(appointment_date, existing_appointment.time)
        requested_end = requested_start + timedelta(minutes=service.duration)
        existing_end = existing_start + timedelta(minutes=service.duration)

        if requested_start < existing_end and existing_start < requested_end:
            return False

    return True


def available_appointment_times(service, appointment_date):
    appointments = list(Appointment.objects.filter(
        service=service,
        date=appointment_date,
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_ACCEPTED],
    ).values_list('time', flat=True))

    available_times = []
    current_datetime = datetime.combine(appointment_date, time(9, 0))
    closing_datetime = datetime.combine(appointment_date, time(18, 0))
    today = timezone.localdate()
    now = timezone.localtime().time().replace(tzinfo=None)

    while current_datetime + timedelta(minutes=service.duration) <= closing_datetime:
        current_time = current_datetime.time()
        requested_end = current_datetime + timedelta(minutes=service.duration)
        is_booked = any(
            current_datetime < datetime.combine(appointment_date, booked_time) + timedelta(minutes=service.duration)
            and datetime.combine(appointment_date, booked_time) < requested_end
            for booked_time in appointments
        )
        is_future_time = appointment_date > today or current_time > now

        if not is_booked and is_future_time:
            available_times.append(current_time)

        current_datetime += timedelta(minutes=30)

    return available_times


def appointment_can_be_cancelled(appointment, now):
    appointment_datetime = datetime.combine(appointment.date, appointment.time)
    current_datetime = datetime.combine(now.date(), now.time().replace(tzinfo=None))
    return appointment.status != Appointment.STATUS_REJECTED and appointment_datetime > current_datetime


@custom_login_required
def my_appointments_view(request):
    appointments = Appointment.objects.filter(user=request.user).select_related('service').order_by('-date', '-time')
    return render(request, 'work/my_appointments.html', {'appointments': appointments})


@custom_login_required
def appointment_detail_view(request, id):
    appointment = get_object_or_404(Appointment.objects.select_related('service'), pk=id, user=request.user)
    now = timezone.localtime()
    can_cancel = appointment_can_be_cancelled(appointment, now)
    return render(request, 'work/appointment_detail.html', {'appointment': appointment, 'today': now.date(), 'can_cancel': can_cancel})


@custom_login_required
def cancel_appointment_view(request, id):
    appointment = get_object_or_404(Appointment.objects.select_related('service'), pk=id, user=request.user)
    now = timezone.localtime()
    can_cancel = appointment_can_be_cancelled(appointment, now)
    if request.method == 'POST' and can_cancel:
        appointment.delete()
        return redirect('my_appointments_view')
    template = 'work/appointment_cancel.html' if can_cancel else 'work/appointment_detail.html'
    context = {'appointment': appointment, 'today': now.date(), 'can_cancel': can_cancel}
    if request.method == 'POST':
        context['error'] = 'Эту запись уже нельзя отменить.'
    return render(request, template, context)


@custom_staff_required
def appointment_management_view(request):
    appointments = Appointment.objects.select_related('user', 'service').order_by('date', 'time')
    return render(request, 'work/appointment_management.html', {
        'appointments': appointments,
        'statuses': Appointment.STATUS_CHOICES,
    })


@custom_staff_required
def update_appointment_status_view(request, id):
    appointment = get_object_or_404(Appointment, pk=id)
    status = request.POST.get('status', '')
    if status not in dict(Appointment.STATUS_CHOICES):
        return redirect('appointment_management_view')
    if status != Appointment.STATUS_REJECTED and not appointment_time_is_available(
        appointment.service,
        appointment.date,
        appointment.time,
        exclude_appointment_id=appointment.pk,
    ):
        return render(request, 'work/appointment_management.html', {
            'appointments': Appointment.objects.select_related('user', 'service').order_by('date', 'time'),
            'statuses': Appointment.STATUS_CHOICES,
            'error': 'Нельзя подтвердить запись: это время уже занято.',
        })
    appointment.status = status
    appointment.save(update_fields=['status'])
    return redirect('appointment_management_view')


