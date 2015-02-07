# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_otp.plugins.otp_email.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text=b'Is this device ready for use?')),
                ('key', models.CharField(default=django_otp.plugins.otp_email.models.default_key, help_text=b'A hex-encoded secret key of up to 20 bytes.', max_length=80, validators=[django_otp.plugins.otp_email.models.key_validator])),
                ('user', models.ForeignKey(help_text=b'The user that this device belongs to.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
