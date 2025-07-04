# Generated by Django 5.2.1 on 2025-06-19 07:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_testimonial_designation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['title'], name='blog_blog_title_d6be1d_idx'),
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['slug'], name='blog_blog_slug_d925e3_idx'),
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['category'], name='blog_blog_categor_8453b3_idx'),
        ),
    ]
