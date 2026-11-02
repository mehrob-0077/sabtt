from django import forms
from .models import Appointment, Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'image', 'location', 'city', 'category']

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if duration < 30 or duration > 480 or duration % 30:
            raise forms.ValidationError('Укажите длительность от 30 до 480 минут с шагом 30 минут.')
        return duration


class AppointmentForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=200, label='Имя клиента')
    note = forms.CharField(required=False, max_length=5000)

    class Meta:
        model = Appointment
        fields = ['customer_name', 'date', 'time', 'note']


