from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sabt', '0009_service_soft_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='customer_name',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
