from django.urls import path
from .views import *

urlpatterns = [
    path('services/', service_list_view, name='service_list_view'),
    path('services/<int:id>/', service_detail_view, name='service_detail_view'),
    path('create/', create_service_view, name='create_service_view'),
    path('update/<int:id>/', update_service_view, name='update_service_view'),
    path('delete/<int:id>/', delete_service_view, name='delete_service_view'),
    path('trash/', view_trash, name='view_trash'),
    path('trash/<int:id>/restore/', restore_product, name='restore_product'),
    path('trash/<int:id>/delete/', hard_delete_product_view, name='hard_delete_product_view'),
    path('categories/', category_list_view, name='category_list_view'),
    path('categories/create/', create_category_view, name='create_category_view'),
    path('categories/<int:id>/', category_detail_view, name='category_detail_view'),
    path('categories/<int:id>/update/', update_category_view, name='update_category_view'),
    path('categories/<int:id>/delete/', delete_category_view, name='delete_category_view'),
    path('services/<int:service_id>/book/', appointment_create_view, name='appointment_create_view'),
    path('appointments/mine/', my_appointments_view, name='my_appointments_view'),
    path('appointments/manage/', appointment_management_view, name='appointment_management_view'),
    path('appointments/manage/<int:id>/status/', update_appointment_status_view, name='update_appointment_status_view'),
    path('appointments/<int:id>/cancel/', cancel_appointment_view, name='cancel_appointment_view'),
    path('appointments/<int:id>/', appointment_detail_view, name='appointment_detail_view'),
]
