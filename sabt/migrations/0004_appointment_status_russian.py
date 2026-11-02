from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sabt', '0003_service_price_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Ожидает'), ('accepted', 'Принята'), ('rejected', 'Отклонена')],
                default='pending',
                max_length=10,
            ),
        ),
    ]