# Generated by Django 2.2.6 on 2019-11-05 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calibration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='standard',
            name='traceability',
            field=models.TextField(default='none'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='standard',
            name='certificate',
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name='StandardLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nominal', models.FloatField()),
                ('actual', models.FloatField()),
                ('uncertainty', models.FloatField()),
                ('standard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calibration.Standard')),
            ],
        ),
    ]
