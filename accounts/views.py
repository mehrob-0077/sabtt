from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import CostumUser, EmailConfirmed
from sabt.models import Appointment, Service


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password1', '')
        confirm_password = request.POST.get('password2', '')

        if not username or not email:
            return render(request, 'auth/register.html', {'error': 'Введите имя пользователя и адрес электронной почты.'})
        if len(username) > 150 or len(email) > 245:
            return render(request, 'auth/register.html', {'error': 'Проверьте длину имени пользователя и адреса электронной почты.'})
        if CostumUser.objects.filter(username__iexact=username).exists():
            return render(request, 'auth/register.html', {'error': 'Это имя пользователя уже занято.'})
        if CostumUser.objects.filter(email__iexact=email).exists():
            return render(request, 'auth/register.html', {'error': 'Этот адрес электронной почты уже зарегистрирован.'})
        if password != confirm_password:
            return render(request, 'auth/register.html', {'error': 'Пароли не совпадают.'})

        user = CostumUser.objects.create_user(email=email, username=username, password=password)
        return render(request, 'auth/register.html', {'success': 'Ссылка для подтверждения отправлена на вашу почту.'})
    return render(request, 'auth/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password1', '')
        user = authenticate(request, email=email, password=password)
        if user is None:
            return render(request, 'auth/login.html', {'error': 'Неверный адрес электронной почты или пароль.'})
        login(request, user)
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and next_url.startswith('/') and not next_url.startswith('//') and '\\' not in next_url:
            return redirect(next_url)
        return redirect('service_list_view')
    return render(request, 'auth/login.html')


@login_required
def home_view(request):
    appointments = Appointment.objects.filter(user=request.user).select_related('service').order_by('date', 'time')
    return render(request, 'auth/home.html', {
        'services_count': Service.objects.filter(is_active=True).count(),
        'appointments_count': appointments.count(),
        'upcoming_appointments': appointments.filter(date__gte=timezone.localdate()).exclude(status=Appointment.STATUS_REJECTED)[:3],
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def confirm_email_view(request, token):
    confirmation = EmailConfirmed.objects.filter(token=token).select_related('user').first()
    if confirmation is None:
        return render(request, 'auth/login.html', {'error': 'Ссылка подтверждения недействительна или уже использована.'})
    user = confirmation.user
    user.is_active = True
    user.save(update_fields=['is_active'])
    confirmation.delete()
    return render(request, 'auth/login.html', {'success': 'Электронная почта подтверждена. Теперь войдите в аккаунт.'})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        password = request.POST.get('password1', '')
        confirm_password = request.POST.get('password2', '')
        user = request.user

        if not user.check_password(old_password):
            return render(request, 'auth/change_password.html', {'error': 'Старый пароль указан неверно.'})
        if password != confirm_password:
            return render(request, 'auth/change_password.html', {'error': 'Пароли не совпадают.'})

        user.set_password(password)
        user.save(update_fields=['password'])
        return redirect('login')
    return render(request, 'auth/change_password.html')


@login_required
def profile_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        if not username:
            error = 'Имя пользователя обязательно.'
        elif len(username) > 150:
            error = 'Имя пользователя не должно быть длиннее 150 символов.'

        if error is None and CostumUser.objects.filter(username__iexact=username).exclude(pk=request.user.pk).exists():
            error = 'Это имя пользователя уже занято.'
        if error is None and CostumUser.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
            error = 'Этот адрес электронной почты уже используется.'
        if error is None and len(email) > 245:
            error = 'Адрес электронной почты слишком длинный.'
        if error is None:
            request.user.username = username
            request.user.email = email
            request.user.save(update_fields=['username', 'email'])
            return redirect('profile_view')
    return render(request, 'auth/profile.html', {'error': error})
