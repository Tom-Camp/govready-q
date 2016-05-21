# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-21 19:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('discussion', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='discussion',
            name='external_participants',
            field=models.ManyToManyField(blank=True, help_text='Additional Users who are participating in this chat, besides those that are members of the Project that contains the Discussion.', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='discussion',
            field=models.ForeignKey(help_text='The Discussion that this comment is attached to.', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='discussion.Discussion'),
        ),
        migrations.AddField(
            model_name='comment',
            name='replies_to',
            field=models.ForeignKey(blank=True, help_text='If this is a reply to a Comment, the Comment that this is in reply to.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='discussion.Comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(help_text='The user making a comment.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='discussion',
            unique_together=set([('attached_to_content_type', 'attached_to_object_id')]),
        ),
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set([('discussion', 'user')]),
        ),
    ]
