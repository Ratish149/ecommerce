# Generated by Django 5.2.1 on 2025-06-22 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_alter_product_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productsubcategory',
            unique_together={('name', 'category')},
        ),
        migrations.AlterUniqueTogether(
            name='productsubsubcategory',
            unique_together={('name', 'subcategory')},
        ),
    ]
