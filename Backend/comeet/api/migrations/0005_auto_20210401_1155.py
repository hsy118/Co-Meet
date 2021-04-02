# Generated by Django 3.0.5 on 2021-04-01 02:55

import api.models
from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_coronaweight_distweight_fpoplweight_recommdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistanceData',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('signgu_nm', models.CharField(max_length=20)),
                ('dist_weights', djongo.models.fields.ArrayField(model_container=api.models.DistWeight)),
            ],
        ),
        migrations.DeleteModel(
            name='RecommData',
        ),
    ]
