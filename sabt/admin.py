from django.contrib import admin
from .models import Appointment, Category, Service


admin.site.register(Service)
admin.site.register(Category)
admin.site.register(Appointment)
