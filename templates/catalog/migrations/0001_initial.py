# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_death', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=200)),
                ('summary', models.TextField(max_length=1000, help_text='Enter a brief description of the book')),
                ('isbn', models.CharField(verbose_name='ISBN', max_length=13, help_text='13 character <a href=https://www.isbn-international.org/content/what-isbn">ISBN number</a>')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Author')),
            ],
        ),
        migrations.CreateModel(
            name='BookInstance',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, help_text='Unique ID for this particular book accross the whole library')),
                ('imprint', models.CharField(max_length=200)),
                ('due_back', models.DateField(blank=True, null=True)),
                ('status', models.CharField(max_length=1, blank=True, default='m', choices=[('m', 'Maintenance'), ('o', 'On load'), ('a', 'Available'), ('r', 'Reserved')], help_text='Book Availability')),
                ('book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Book')),
            ],
            options={
                'ordering': ['due_back'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200, help_text='Enter a book genre (eg. Science Fiction, French Poetry etc.)')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(help_text='select a genre for this book', to='catalog.Genre'),
        ),
    ]
