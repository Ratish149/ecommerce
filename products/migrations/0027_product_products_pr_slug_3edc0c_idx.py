# Generated by Django 5.2.1 on 2025-06-17 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_product_products_pr_name_9ff0a3_idx_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='products_pr_slug_3edc0c_idx'),
        ),
    ]
