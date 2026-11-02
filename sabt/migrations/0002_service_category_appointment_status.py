import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


def copy_appointment_statuses(apps, schema_editor):
    Appointment = apps.get_model('sabt', 'Appointment')
    database = schema_editor.connection.alias
    for appointment in Appointment.objects.using(database).all().iterator():
        appointment.status_new = 'accepted' if appointment.status else 'pending'
        appointment.save(using=database, update_fields=['status_new'])


def restore_appointment_statuses(apps, schema_editor):
    Appointment = apps.get_model('sabt', 'Appointment')
    database = schema_editor.connection.alias
    for appointment in Appointment.objects.using(database).all().iterator():
        appointment.status = appointment.status_new == 'accepted'
        appointment.save(using=database, update_fields=['status'])


class Migration(migrations.Migration):

    dependencies = [
        ('sabt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='sabt.category'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='status_new',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
        migrations.RunPython(copy_appointment_statuses, restore_appointment_statuses),
        migrations.RemoveField(
            model_name='appointment',
            name='status',
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='status_new',
            new_name='status',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.UniqueConstraint(condition=~Q(status='rejected'), fields=('service', 'date', 'time'), name='unique_active_appointment_slot'),
        ),
    ]
