# Generated by Django 5.1.1 on 2025-03-30 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("token", models.CharField(max_length=200)),
                ("refresh_token", models.CharField(max_length=200)),
                ("update_time", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
