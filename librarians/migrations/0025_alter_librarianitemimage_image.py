# Generated by Django 4.2.19 on 2025-04-18 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarians', '0024_remove_librarianitem_image_librarianitemimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librarianitemimage',
            name='image',
            field=models.ImageField(blank=True, default='boardgame_pics/default_boardgame.jpg', null=True, upload_to='boardgame_pics'),
        ),
    ]
