# Generated by Django 4.2.19 on 2025-03-30 01:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('librarians', '0015_alter_librarianitem_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionAccessRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_requests', to='librarians.collection')),
                ('patron', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
