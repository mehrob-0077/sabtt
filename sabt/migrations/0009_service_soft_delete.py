from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sabt', '0008_delete_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='service',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
