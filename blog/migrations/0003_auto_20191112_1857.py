# Generated by Django 2.2.6 on 2019-11-12 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_comment_sub_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='sub_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Substitute'),
        ),
    ]
